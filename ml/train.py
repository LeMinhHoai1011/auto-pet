"""Train a 96x96 grayscale classifier and export an int8 MCU model."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--output", type=Path, default=Path("ml/output"))
    parser.add_argument("--epochs", type=int, default=30)
    args = parser.parse_args()
    classes = ["none", "cat", "dog"]
    for split in ("train", "val", "test"):
        for label in classes:
            folder = args.dataset / split / label
            if not folder.is_dir() or not any(
                p.suffix.lower() in (".jpg", ".jpeg", ".png", ".bmp")
                for p in folder.iterdir()
            ):
                parser.error(f"Missing images: {folder}")

    import numpy as np
    import tensorflow as tf

    tf.keras.utils.set_random_seed(42)

    def load(split, shuffle):
        ds = tf.keras.utils.image_dataset_from_directory(
            args.dataset / split, class_names=classes, color_mode="grayscale",
            image_size=(96, 96), interpolation="nearest", batch_size=32,
            shuffle=shuffle, seed=42,
        )
        return ds.map(lambda x, y: (x / 255.0, y)).prefetch(1)

    train, val, test = load("train", True), load("val", False), load("test", False)
    model = tf.keras.Sequential([
        tf.keras.layers.Input((96, 96, 1)),
        tf.keras.layers.Conv2D(4, 3, strides=2, padding="same", activation="relu"),
        tf.keras.layers.MaxPooling2D(2),
        tf.keras.layers.Conv2D(8, 3, strides=2, padding="same", activation="relu"),
        tf.keras.layers.MaxPooling2D(2),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(3, activation="softmax"),
    ])
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy",
                  metrics=["accuracy"])
    model.fit(train, validation_data=val, epochs=args.epochs, callbacks=[
        tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True),
    ])
    args.output.mkdir(parents=True, exist_ok=True)
    model.save(args.output / "pet.keras")

    def representative():
        for batch, _ in train.take(10):
            for sample in batch:
                yield [sample[None, ...]]

    model.export(str(args.output / "saved_model"))
    converter = tf.lite.TFLiteConverter.from_saved_model(str(args.output / "saved_model"))
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.representative_dataset = representative
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8
    data = converter.convert()
    (args.output / "pet.tflite").write_bytes(data)

    interpreter = tf.lite.Interpreter(model_content=data)
    interpreter.allocate_tensors()
    inp, out = interpreter.get_input_details()[0], interpreter.get_output_details()[0]
    scale, zero = inp["quantization"]
    confusion = np.zeros((3, 3), dtype=int)
    for images, labels in test:
        for image, label in zip(images.numpy(), labels.numpy()):
            quantized = np.clip(np.rint(image / scale + zero), -128, 127).astype(np.int8)
            interpreter.set_tensor(inp["index"], quantized[None, ...])
            interpreter.invoke()
            pred = int(np.argmax(interpreter.get_tensor(out["index"])[0]))
            confusion[int(label), pred] += 1
    metrics = {
        "classes": classes, "test_confusion_matrix": confusion.tolist(),
        "test_int8_accuracy": float(confusion.trace() / confusion.sum()),
        "input_quantization": [scale, zero], "model_bytes": len(data),
    }
    (args.output / "metrics.json").write_text(json.dumps(metrics, indent=2))
    lines = [", ".join(f"0x{b:02x}" for b in data[i:i+12])
             for i in range(0, len(data), 12)]
    header = ("#pragma once\n#include <stdint.h>\n"
              "alignas(16) const unsigned char pet_model_data[] = {\n" +
              ",\n".join(lines) + "\n};\n")
    (args.output / "model_data.h").write_text(header)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
