#include "pet_detect.h"
#include "config_cam.h"
#include <Arduino.h>
#include <math.h>

// ─────────────────────────────────────────────
//  Chế độ 1: TFLite Micro (khi HAS_TFLITE_MODEL=1)
// ─────────────────────────────────────────────
#if HAS_TFLITE_MODEL

#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/schema/schema_generated.h"
#include "model_data.h"

static const tflite::Model* model = nullptr;
static tflite::MicroInterpreter* interpreter = nullptr;
static TfLiteTensor* inputTensor = nullptr;
static TfLiteTensor* outputTensor = nullptr;

static constexpr int kTensorArenaSize = 96 * 1024;
static uint8_t tensorArena[kTensorArenaSize] __attribute__((aligned(16)));

static const char* classLabels[NUM_CLASSES] = {"none", "cat", "dog"};

// RGB565 → grayscale, resize nearest-neighbor
static void preprocess(const uint8_t* rgb565, int srcW, int srcH,
                       int8_t* dst, int dstW, int dstH) {
    for (int dy = 0; dy < dstH; dy++) {
        int sy = dy * srcH / dstH;
        for (int dx = 0; dx < dstW; dx++) {
            int sx = dx * srcW / dstW;
            int idx = (sy * srcW + sx) * 2;
            uint16_t pix = (rgb565[idx] << 8) | rgb565[idx + 1];

            uint8_t r = ((pix >> 11) & 0x1F) * 255 / 31;
            uint8_t g = ((pix >> 5)  & 0x3F) * 255 / 63;
            uint8_t b = ( pix        & 0x1F) * 255 / 31;

            uint8_t gray = (r * 77 + g * 150 + b * 29) >> 8;
            int q = (int)roundf((gray / 255.0f) / inputTensor->params.scale) +
                    inputTensor->params.zero_point;
            dst[dy * dstW + dx] = (int8_t)constrain(q, -128, 127);
        }
    }
}

bool petDetectInit() {
    model = tflite::GetModel(pet_model_data);
    if (model->version() != TFLITE_SCHEMA_VERSION) {
        Serial.println("[TFLITE] Model version mismatch");
        return false;
    }

    static tflite::MicroMutableOpResolver<6> resolver;
    resolver.AddConv2D();
    resolver.AddDepthwiseConv2D();
    resolver.AddReshape();
    resolver.AddSoftmax();
    resolver.AddFullyConnected();
    resolver.AddMaxPool2D();

    static tflite::MicroInterpreter staticInterp(model, resolver,
                                                   tensorArena, kTensorArenaSize);
    interpreter = &staticInterp;

    if (interpreter->AllocateTensors() != kTfLiteOk) {
        Serial.println("[TFLITE] AllocateTensors failed");
        return false;
    }

    inputTensor  = interpreter->input(0);
    outputTensor = interpreter->output(0);

    if (inputTensor->type != kTfLiteInt8 || outputTensor->type != kTfLiteInt8 ||
        inputTensor->dims->size != 4 || inputTensor->dims->data[0] != 1 ||
        inputTensor->dims->data[1] != MODEL_INPUT_H ||
        inputTensor->dims->data[2] != MODEL_INPUT_W ||
        inputTensor->dims->data[3] != MODEL_INPUT_CH ||
        outputTensor->bytes != NUM_CLASSES || inputTensor->params.scale <= 0) {
        Serial.println("[TFLITE] Unsupported tensor layout or quantization");
        interpreter = nullptr;
        return false;
    }

    Serial.printf("[TFLITE] Ready — input %dx%dx%d, arena %d bytes\n",
                  inputTensor->dims->data[1], inputTensor->dims->data[2],
                  inputTensor->dims->data[3], kTensorArenaSize);
    return true;
}

PetResult petDetectRun(const uint8_t* buf, size_t len, int w, int h) {
    PetResult res = {false, "none", 0};
    if (!interpreter || !buf || w <= 0 || h <= 0 ||
        len < (size_t)w * h * 2) return res;

    preprocess(buf, w, h, inputTensor->data.int8,
               MODEL_INPUT_W, MODEL_INPUT_H);

    if (interpreter->Invoke() != kTfLiteOk) {
        Serial.println("[TFLITE] Invoke failed");
        return res;
    }

    int bestIdx = 0;
    int8_t bestVal = outputTensor->data.int8[0];
    for (int i = 1; i < NUM_CLASSES; i++) {
        if (outputTensor->data.int8[i] > bestVal) {
            bestVal = outputTensor->data.int8[i];
            bestIdx = i;
        }
    }

    float scale  = outputTensor->params.scale;
    int   zp     = outputTensor->params.zero_point;
    float conf   = (bestVal - zp) * scale;

    res.label      = classLabels[bestIdx];
    res.confidence  = conf;
    res.detected    = (bestIdx != CLASS_BACKGROUND && conf >= PET_CONFIDENCE_MIN);

    Serial.printf("[TFLITE] %s %.0f%%\n", res.label, conf * 100);
    return res;
}

// ─────────────────────────────────────────────
//  Chế độ 2: Frame differencing (mặc định)
//  PIR đã phát hiện chuyển động → camera xác nhận
//  có vật thể di chuyển (không phân biệt loài)
// ─────────────────────────────────────────────
#else

static uint8_t* refFrame = nullptr;
static size_t   refLen   = 0;
static bool     hasRef   = false;

bool petDetectInit() {
    Serial.println("[DETECT] Frame-diff mode (no TFLite model)");
    hasRef = false;
    return true;
}

PetResult petDetectRun(const uint8_t* buf, size_t len, int w, int h) {
    PetResult res = {false, "none", 0};
    if (!buf || w <= 0 || h <= 0 || len < (size_t)w * h * 2) return res;

    // Frame đầu tiên → lưu làm reference (nền)
    if (!hasRef) {
        if (refFrame) free(refFrame);
        refFrame = (uint8_t*)ps_malloc(len);
        if (!refFrame) {
            refFrame = (uint8_t*)malloc(len);
        }
        if (refFrame) {
            memcpy(refFrame, buf, len);
            refLen = len;
            hasRef = true;
            Serial.println("[DETECT] Reference frame saved");
        }
        return res;
    }

    if (len != refLen) return res;

    // So sánh grayscale từ RGB565
    int totalPixels = w * h;
    int changedPixels = 0;

    for (int i = 0; i < totalPixels; i++) {
        int idx = i * 2;
        uint16_t pix1 = (buf[idx] << 8) | buf[idx + 1];
        uint16_t pix2 = (refFrame[idx] << 8) | refFrame[idx + 1];

        uint8_t g1 = ((pix1 >> 5) & 0x3F) * 255 / 63;
        uint8_t g2 = ((pix2 >> 5) & 0x3F) * 255 / 63;

        int diff = abs((int)g1 - (int)g2);
        if (diff > MOTION_PIXEL_THRESH) changedPixels++;
    }

    float pct = (float)changedPixels * 100.0f / totalPixels;

    // Cập nhật reference cho lần sau
    memcpy(refFrame, buf, len);

    Serial.printf("[DETECT] Changed: %.1f%% (threshold: %d%%)\n",
                  pct, MOTION_AREA_PCT);

    if (pct >= MOTION_AREA_PCT) {
        res.detected   = true;
        res.label      = "motion";
        res.confidence = min(pct / 50.0f, 1.0f);
    }

    return res;
}

#endif
