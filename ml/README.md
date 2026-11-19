# Train model ESP32-CAM

Chưa có bộ ảnh hoặc model đã train. Firmware mặc định vẫn dùng frame differencing:
chỉ xác nhận chuyển động, không phân biệt mèo/chó.

## Chuẩn bị ảnh thật

Tạo `dataset/{train,val,test}/{none,cat,dog}/` với ảnh JPG/PNG.
`none` gồm bát trống, người, bóng, thay đổi ánh sáng và vật thể không phải thú cưng.
Chụp từ vị trí camera thực tế, nhiều giờ và khoảng cách; nên có vài trăm ảnh mỗi lớp.
Chia theo **buổi quay/ngày quay**, không chia ngẫu nhiên các frame gần nhau của cùng
video vào nhiều tập. Gợi ý 70% train, 15% val, 15% test; mỗi tập cần đủ ba lớp.

## Chạy (Python 3.11)

```powershell
python -m venv ml/.venv
ml/.venv/Scripts/python -m pip install -r ml/requirements.txt
ml/.venv/Scripts/python ml/train.py dataset --epochs 30
```

Xuất `ml/output/pet.keras`, `pet.tflite`, `model_data.h`, `metrics.json`.
Thứ tự lớp luôn là `none, cat, dog`; đầu vào 96×96×1 grayscale trong [0,1],
đầu vào/ra TFLite int8. Báo cáo kiểm tra model int8 trên tập test độc lập.
Quy trình quantization theo [tài liệu Google AI Edge](https://developers.google.com/edge/litert/conversion/tensorflow/quantization/post_training_quantization).

## Tích hợp sau khi có dữ liệu

1. Kiểm tra confusion matrix, nhất là `none` bị đoán nhầm thành cat/dog.
2. Copy `ml/output/model_data.h` sang `cam/model_data.h`.
3. Cài thư viện TensorFlow Lite Micro tương thích Arduino ESP32, bổ sung vào
   `lib_deps` của env `esp32cam`, đổi `HAS_TFLITE_MODEL=1` trong `platformio.ini`.
   Repo hiện **chưa cung cấp thư viện TFLM**, nên chưa thể build chế độ model ngay.
4. Build `pio run -e esp32cam`; kiểm tra AllocateTensors với arena 96 KiB,
   thời gian inference, bộ nhớ và độ chính xác trên camera thật trước khi cho ăn tự động.

Chưa chạy train/export vì chưa có dữ liệu; chưa xác minh op converter và dung lượng
arena trên thiết bị. Không coi accuracy trên train là kết quả kiểm chứng thực tế.
