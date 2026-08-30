"""
Random Forest baseline for Dataset V2.1.

Uses the same model configuration as V2 so improvements
come from better simulation and features—not hidden tuning.
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

from backend.ai.preprocessing_v2_1 import (
    load_data,
    preprocess_data,
)


MODEL_DIRECTORY = Path("models")

MODEL_PATH = (
    MODEL_DIRECTORY
    / "fault_classifier_v2_1.joblib"
)

METRICS_PATH = (
    MODEL_DIRECTORY
    / "fault_classifier_v2_1_metrics.json"
)


def create_model():
    """
    Keep the V2 configuration for a fair comparison.
    """

    return RandomForestClassifier(
        n_estimators=300,
        max_depth=14,
        min_samples_leaf=3,
        max_features="sqrt",
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=-1,
    )


def train_model():

    print("=" * 70)
    print("DATASET V2.1 FAULT CLASSIFICATION")
    print("=" * 70)

    dataset = load_data()
    prepared = preprocess_data(dataset)

    model = create_model()

    print("\nTraining V2.1 Random Forest...")

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

    label_encoder = prepared[
        "label_encoder"
    ]

    class_names = label_encoder.classes_
    class_numbers = np.arange(
        len(class_names)
    )

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

    print("\n" + "=" * 70)
    print("V2.1 UNSEEN-RUN RESULTS")
    print("=" * 70)

    print(
        f"Accuracy          : "
        f"{accuracy * 100:.2f}%"
    )

    print(
        f"Balanced Accuracy : "
        f"{balanced_accuracy * 100:.2f}%"
    )

    print(
        f"Macro F1          : "
        f"{macro_f1:.4f}"
    )

    print("\nClassification Report:")
    print(report_text)

    print("Confusion Matrix:")
    print(matrix)

    feature_importance = sorted(
        zip(
            prepared["features"],
            model.feature_importances_,
        ),
        key=lambda item: item[1],
        reverse=True,
    )

    print("\nFeature Importance:")

    for feature, importance in (
        feature_importance
    ):
        print(
            f"{feature:<24}: "
            f"{importance:.4f}"
        )

    MODEL_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_bundle = {
        "model": model,
        "label_encoder": label_encoder,
        "scaler": prepared["scaler"],
        "features": prepared["features"],
        "train_run_ids": (
            prepared["train_run_ids"]
        ),
        "test_run_ids": (
            prepared["test_run_ids"]
        ),
        "dataset_version": "V2.1",
        "rows_per_run": 400,
        "rolling_window": 10,
    }

    joblib.dump(
        model_bundle,
        MODEL_PATH,
    )

    metrics = {
        "dataset_version": "V2.1",
        "split_method": (
            "40 complete training runs and "
            "10 complete unseen testing runs"
        ),
        "accuracy": float(accuracy),
        "balanced_accuracy": float(
            balanced_accuracy
        ),
        "macro_f1": float(macro_f1),
        "class_names": class_names.tolist(),
        "confusion_matrix": matrix.tolist(),
        "classification_report": report_data,
        "features": prepared["features"],
        "train_run_ids": (
            prepared["train_run_ids"]
        ),
        "test_run_ids": (
            prepared["test_run_ids"]
        ),
        "feature_importance": {
            feature: float(importance)
            for feature, importance
            in feature_importance
        },
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


if __name__ == "__main__":
    train_model()