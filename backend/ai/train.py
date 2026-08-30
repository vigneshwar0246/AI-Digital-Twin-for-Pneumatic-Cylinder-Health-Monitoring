"""
Dataset V2 Random Forest fault classifier.

Trains only on physical sensor measurements and evaluates
using five completely unseen simulation runs.
"""

import json
from pathlib import Path

import joblib
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)

from backend.ai.preprocessing import (
    load_data,
    preprocess_data,
)


MODEL_DIRECTORY = Path("models")
MODEL_PATH = MODEL_DIRECTORY / "fault_classifier_v2.joblib"
METRICS_PATH = MODEL_DIRECTORY / "fault_classifier_v2_metrics.json"


def train_model():
    print("=" * 60)
    print("DATASET V2 FAULT CLASSIFICATION")
    print("=" * 60)

    dataset = load_data()
    prepared = preprocess_data(dataset)

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=14,
        min_samples_leaf=3,
        max_features="sqrt",
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=-1,
    )

    print("\nTraining Random Forest...")
    model.fit(
        prepared["X_train"],
        prepared["y_train"],
    )

    predictions = model.predict(
        prepared["X_test"]
    )

    accuracy = accuracy_score(
        prepared["y_test"],
        predictions,
    )

    balanced_accuracy = balanced_accuracy_score(
        prepared["y_test"],
        predictions,
    )

    macro_f1 = f1_score(
        prepared["y_test"],
        predictions,
        average="macro",
    )

    label_encoder = prepared["label_encoder"]
    class_names = label_encoder.classes_
    class_numbers = np.arange(len(class_names))

    report_text = classification_report(
        prepared["y_test"],
        predictions,
        labels=class_numbers,
        target_names=class_names,
        zero_division=0,
    )

    report_data = classification_report(
        prepared["y_test"],
        predictions,
        labels=class_numbers,
        target_names=class_names,
        zero_division=0,
        output_dict=True,
    )

    matrix = confusion_matrix(
        prepared["y_test"],
        predictions,
        labels=class_numbers,
    )

    print("\n" + "=" * 60)
    print("UNSEEN-RUN TEST RESULTS")
    print("=" * 60)

    print(f"Accuracy          : {accuracy * 100:.2f}%")
    print(
        f"Balanced Accuracy : "
        f"{balanced_accuracy * 100:.2f}%"
    )
    print(f"Macro F1 Score    : {macro_f1:.4f}")

    print("\nClassification Report:")
    print(report_text)

    print("Confusion Matrix:")
    print(matrix)

    print("\nFeature Importance:")

    importance_values = sorted(
        zip(
            prepared["features"],
            model.feature_importances_,
        ),
        key=lambda item: item[1],
        reverse=True,
    )

    for feature, importance in importance_values:
        print(f"{feature:<15}: {importance:.4f}")

    MODEL_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_bundle = {
        "model": model,
        "label_encoder": label_encoder,
        "scaler": prepared["scaler"],
        "features": prepared["features"],
        "train_run_ids": prepared["train_run_ids"],
        "test_run_ids": prepared["test_run_ids"],
        "dataset_version": "V2",
        "rows_per_run": 400,
    }

    joblib.dump(
        model_bundle,
        MODEL_PATH,
    )

    metrics = {
        "dataset_version": "V2",
        "split_method": (
            "20 complete training runs and "
            "5 complete unseen testing runs"
        ),
        "accuracy": float(accuracy),
        "balanced_accuracy": float(balanced_accuracy),
        "macro_f1": float(macro_f1),
        "class_names": class_names.tolist(),
        "confusion_matrix": matrix.tolist(),
        "classification_report": report_data,
        "features": prepared["features"],
        "train_run_ids": prepared["train_run_ids"],
        "test_run_ids": prepared["test_run_ids"],
    }

    with open(
        METRICS_PATH,
        "w",
        encoding="utf-8",
    ) as metrics_file:
        json.dump(
            metrics,
            metrics_file,
            indent=4,
        )

    print("\nModel saved to:")
    print(MODEL_PATH)

    print("\nMetrics saved to:")
    print(METRICS_PATH)

    return model_bundle, metrics


if __name__ == "__main__":
    train_model()