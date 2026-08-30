"""
Five-fold run-level evaluation for Dataset V2.

Every fold tests on five complete unseen runs:
one run from each planned operating condition.
"""

import json
from pathlib import Path

import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler

from backend.ai.preprocessing import (
    FEATURE_COLUMNS,
    create_run_table,
    load_data,
)


OUTPUT_PATH = Path(
    "models/fault_classifier_v2_cv_metrics.json"
)


def create_model():
    return RandomForestClassifier(
        n_estimators=300,
        max_depth=14,
        min_samples_leaf=3,
        max_features="sqrt",
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=-1,
    )


def evaluate_model():
    print("=" * 70)
    print("DATASET V2 FIVE-FOLD UNSEEN-RUN EVALUATION")
    print("=" * 70)

    df = load_data()
    run_table = create_run_table(df)

    label_encoder = LabelEncoder()
    label_encoder.fit(df["Fault"])

    class_names = label_encoder.classes_
    class_numbers = np.arange(len(class_names))

    splitter = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42,
    )

    fold_results = []
    all_true = []
    all_predictions = []

    split_data = splitter.split(
        run_table["RunID"],
        run_table["RunFault"],
    )

    for fold_number, (
        train_indices,
        test_indices,
    ) in enumerate(split_data, start=1):

        train_runs = run_table.iloc[
            train_indices
        ]

        test_runs = run_table.iloc[
            test_indices
        ]

        train_run_ids = train_runs[
            "RunID"
        ].tolist()

        test_run_ids = test_runs[
            "RunID"
        ].tolist()

        train_df = df[
            df["RunID"].isin(train_run_ids)
        ]

        test_df = df[
            df["RunID"].isin(test_run_ids)
        ]

        X_train = train_df[FEATURE_COLUMNS]
        X_test = test_df[FEATURE_COLUMNS]

        y_train = label_encoder.transform(
            train_df["Fault"]
        )

        y_test = label_encoder.transform(
            test_df["Fault"]
        )

        scaler = StandardScaler()

        X_train_scaled = scaler.fit_transform(
            X_train
        )

        X_test_scaled = scaler.transform(
            X_test
        )

        model = create_model()

        model.fit(
            X_train_scaled,
            y_train,
        )

        predictions = model.predict(
            X_test_scaled
        )

        accuracy = accuracy_score(
            y_test,
            predictions,
        )

        balanced_accuracy = balanced_accuracy_score(
            y_test,
            predictions,
        )

        macro_f1 = f1_score(
            y_test,
            predictions,
            average="macro",
        )

        class_recall = recall_score(
            y_test,
            predictions,
            labels=class_numbers,
            average=None,
            zero_division=0,
        )

        all_true.extend(y_test.tolist())
        all_predictions.extend(
            predictions.tolist()
        )

        recall_dictionary = {
            class_name: float(recall_value)
            for class_name, recall_value in zip(
                class_names,
                class_recall,
            )
        }

        fold_results.append({
            "fold": fold_number,
            "train_run_ids": train_run_ids,
            "test_run_ids": test_run_ids,
            "test_run_conditions": (
                test_runs[
                    ["RunID", "RunFault"]
                ].to_dict(orient="records")
            ),
            "accuracy": float(accuracy),
            "balanced_accuracy": float(
                balanced_accuracy
            ),
            "macro_f1": float(macro_f1),
            "class_recall": recall_dictionary,
        })

        print("\n" + "-" * 70)
        print(f"FOLD {fold_number}")
        print("-" * 70)

        print("Testing runs:")
        print(
            test_runs[
                ["RunID", "RunFault"]
            ].sort_values("RunFault").to_string(
                index=False
            )
        )

        print(
            f"\nAccuracy          : "
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

        print("\nRecall by class:")

        for class_name, recall_value in zip(
            class_names,
            class_recall,
        ):
            print(
                f"{class_name:<18}: "
                f"{recall_value * 100:.2f}%"
            )

    accuracy_values = np.array([
        result["accuracy"]
        for result in fold_results
    ])

    balanced_values = np.array([
        result["balanced_accuracy"]
        for result in fold_results
    ])

    f1_values = np.array([
        result["macro_f1"]
        for result in fold_results
    ])

    aggregate_matrix = confusion_matrix(
        all_true,
        all_predictions,
        labels=class_numbers,
    )

    average_class_recall = {}

    for class_name in class_names:
        values = [
            result["class_recall"][class_name]
            for result in fold_results
        ]

        average_class_recall[class_name] = float(
            np.mean(values)
        )

    print("\n" + "=" * 70)
    print("FIVE-FOLD SUMMARY")
    print("=" * 70)

    print(
        f"Accuracy          : "
        f"{accuracy_values.mean() * 100:.2f}% "
        f"± {accuracy_values.std() * 100:.2f}%"
    )

    print(
        f"Balanced Accuracy : "
        f"{balanced_values.mean() * 100:.2f}% "
        f"± {balanced_values.std() * 100:.2f}%"
    )

    print(
        f"Macro F1          : "
        f"{f1_values.mean():.4f} "
        f"± {f1_values.std():.4f}"
    )

    print("\nAverage recall by class:")

    for class_name, recall_value in (
        average_class_recall.items()
    ):
        print(
            f"{class_name:<18}: "
            f"{recall_value * 100:.2f}%"
        )

    print("\nAggregate Confusion Matrix:")
    print(aggregate_matrix)

    output = {
        "dataset_version": "V2",
        "evaluation": (
            "Five-fold stratified evaluation "
            "using complete unseen runs"
        ),
        "features": FEATURE_COLUMNS,
        "accuracy_mean": float(
            accuracy_values.mean()
        ),
        "accuracy_std": float(
            accuracy_values.std()
        ),
        "balanced_accuracy_mean": float(
            balanced_values.mean()
        ),
        "balanced_accuracy_std": float(
            balanced_values.std()
        ),
        "macro_f1_mean": float(
            f1_values.mean()
        ),
        "macro_f1_std": float(
            f1_values.std()
        ),
        "average_class_recall": (
            average_class_recall
        ),
        "aggregate_confusion_matrix": (
            aggregate_matrix.tolist()
        ),
        "folds": fold_results,
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as output_file:
        json.dump(
            output,
            output_file,
            indent=4,
        )

    print("\nCross-validation results saved to:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    evaluate_model()