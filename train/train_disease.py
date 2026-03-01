import argparse
import json
from pathlib import Path

import numpy as np
import tensorflow as tf


def build_model(num_classes: int, image_size: int) -> tf.keras.Model:
    base = tf.keras.applications.MobileNetV2(
        input_shape=(image_size, image_size, 3),
        include_top=False,
        weights="imagenet",
    )
    base.trainable = False

    inputs = tf.keras.Input(shape=(image_size, image_size, 3))
    x = tf.keras.applications.mobilenet_v2.preprocess_input(inputs)
    x = base(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax")(x)

    model = tf.keras.Model(inputs, outputs)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train baseline MobileNetV2 disease classifier.")
    parser.add_argument("--dataset-dir", required=True, help="Path to disease image folder by class subdirectories.")
    parser.add_argument("--output-model", default="models/disease_model.h5", help="Path to output .h5 model.")
    parser.add_argument("--output-labels", default="models/disease_labels.json", help="Path to labels json.")
    parser.add_argument("--output-metrics", default="models/disease_metrics.json", help="Path to metrics json.")
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tf.random.set_seed(args.seed)
    np.random.seed(args.seed)

    dataset_dir = Path(args.dataset_dir)
    if not dataset_dir.exists():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")

    train_ds = tf.keras.preprocessing.image_dataset_from_directory(
        dataset_dir,
        validation_split=0.2,
        subset="training",
        seed=args.seed,
        image_size=(args.image_size, args.image_size),
        batch_size=args.batch_size,
    )
    val_ds = tf.keras.preprocessing.image_dataset_from_directory(
        dataset_dir,
        validation_split=0.2,
        subset="validation",
        seed=args.seed,
        image_size=(args.image_size, args.image_size),
        batch_size=args.batch_size,
    )

    class_names = train_ds.class_names
    num_classes = len(class_names)
    if num_classes < 2:
        raise ValueError("Need at least 2 classes in dataset.")

    augment = tf.keras.Sequential(
        [
            tf.keras.layers.RandomFlip("horizontal"),
            tf.keras.layers.RandomRotation(0.08),
            tf.keras.layers.RandomZoom(0.1),
            tf.keras.layers.RandomContrast(0.1),
        ]
    )

    autotune = tf.data.AUTOTUNE
    train_ds = train_ds.map(lambda x, y: (augment(x), y), num_parallel_calls=autotune).prefetch(autotune)
    val_ds = val_ds.prefetch(autotune)

    model = build_model(num_classes=num_classes, image_size=args.image_size)
    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True),
    ]
    history = model.fit(train_ds, validation_data=val_ds, epochs=args.epochs, callbacks=callbacks, verbose=1)

    val_loss, val_acc = model.evaluate(val_ds, verbose=0)

    output_model = Path(args.output_model)
    output_labels = Path(args.output_labels)
    output_metrics = Path(args.output_metrics)
    output_model.parent.mkdir(parents=True, exist_ok=True)

    model.save(output_model)

    labels_payload = {"classes": class_names}
    output_labels.write_text(json.dumps(labels_payload, indent=2), encoding="utf-8")

    metrics_payload = {
        "val_loss": float(val_loss),
        "val_accuracy": float(val_acc),
        "epochs_ran": int(len(history.history.get("loss", []))),
    }
    output_metrics.write_text(json.dumps(metrics_payload, indent=2), encoding="utf-8")

    print("Training completed.")
    print(f"Saved model: {output_model}")
    print(f"Saved labels: {output_labels}")
    print(f"Saved metrics: {output_metrics}")


if __name__ == "__main__":
    main()
