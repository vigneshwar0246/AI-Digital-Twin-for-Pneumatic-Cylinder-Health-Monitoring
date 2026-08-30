"""
Leakage-free preprocessing for Dataset V2.1.

Uses the actual metadata RunID and keeps complete
simulation runs separated during training and testing.
"""

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import (
    LabelEncoder,
    StandardScaler,
)

from backend.ai.feature_engineering_v2_1 import (
    FEATURE_COLUMNS,
    add_temporal_features,
)


DATASET_PATH = (
    "datasets/simulated/"
    "pneumatic_cylinder_dataset_v2_1.csv"
)

METADATA_PATH = (
    "datasets/simulated/"
    "pneumatic_cylinder_dataset_v2_1_metadata.csv"
)

TEST_RUN_COUNT = 10


def load_data():
    """Load and align Dataset V2.1 with its metadata."""

    dataset = pd.read_csv(DATASET_PATH)
    metadata = pd.read_csv(METADATA_PATH)

    if len(dataset) != len(metadata):
        raise ValueError(
            "Dataset and metadata row counts differ."
        )

    if not dataset["Time"].equals(
        metadata["Time"]
    ):
        raise ValueError(
            "Dataset and metadata timestamps do not align."
        )

    df = dataset.copy()

    df["RunID"] = metadata["RunID"]
    df["Step"] = metadata["Step"]
    df["PlannedFault"] = metadata[
        "PlannedFault"
    ]

    df = add_temporal_features(df)

    print("=" * 64)
    print("DATASET V2.1 LOADED")
    print("=" * 64)

    print("Rows:", len(df))
    print(
        "Independent runs:",
        df["RunID"].nunique(),
    )
    print(
        "Model features:",
        len(FEATURE_COLUMNS),
    )

    return df


def create_run_table(df):
    """Create one stratification row per simulation run."""

    condition_counts = (
        df.groupby("RunID")[
            "PlannedFault"
        ].nunique()
    )

    if not condition_counts.eq(1).all():
        raise ValueError(
            "A run contains multiple planned conditions."
        )

    run_table = (
        df.groupby("RunID")[
            "PlannedFault"
        ]
        .first()
        .reset_index(name="RunFault")
    )

    print("\nRuns by planned condition:")
    print(
        run_table["RunFault"].value_counts()
    )

    return run_table


def preprocess_data(df):
    """
    Select two complete runs per condition for testing.

    The remaining eight runs per condition are used
    for training.
    """

    run_table = create_run_table(df)

    train_runs, test_runs = train_test_split(
        run_table,
        test_size=TEST_RUN_COUNT,
        random_state=42,
        stratify=run_table["RunFault"],
    )

    train_run_ids = sorted(
        train_runs["RunID"].tolist()
    )

    test_run_ids = sorted(
        test_runs["RunID"].tolist()
    )

    if set(train_run_ids) & set(test_run_ids):
        raise ValueError(
            "Run leakage detected."
        )

    train_df = df[
        df["RunID"].isin(train_run_ids)
    ].copy()

    test_df = df[
        df["RunID"].isin(test_run_ids)
    ].copy()

    X_train = train_df[FEATURE_COLUMNS]
    X_test = test_df[FEATURE_COLUMNS]

    label_encoder = LabelEncoder()

    y_train = label_encoder.fit_transform(
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

    print("\n" + "=" * 64)
    print("DATASET V2.1 LEAKAGE-FREE SPLIT")
    print("=" * 64)

    print("Training runs:", len(train_run_ids))
    print("Testing runs :", len(test_run_ids))

    print("\nTesting run conditions:")
    print(
        test_runs[
            ["RunID", "RunFault"]
        ]
        .sort_values(
            ["RunFault", "RunID"]
        )
        .to_string(index=False)
    )

    print("\nTraining samples:", len(train_df))
    print("Testing samples :", len(test_df))

    print("\nFeatures used:")

    for feature in FEATURE_COLUMNS:
        print("-", feature)

    print("\nExcluded from model:")
    print("- Time")
    print("- CycleCount")
    print("- Health")
    print("- Fault")
    print("- RunID")
    print("- Step")
    print("- PlannedFault")
    print("- Severity and all simulation metadata")

    return {
        "X_train": X_train_scaled,
        "X_test": X_test_scaled,
        "y_train": y_train,
        "y_test": y_test,
        "label_encoder": label_encoder,
        "scaler": scaler,
        "features": FEATURE_COLUMNS,
        "train_run_ids": train_run_ids,
        "test_run_ids": test_run_ids,
    }


if __name__ == "__main__":
    data = load_data()
    preprocess_data(data)