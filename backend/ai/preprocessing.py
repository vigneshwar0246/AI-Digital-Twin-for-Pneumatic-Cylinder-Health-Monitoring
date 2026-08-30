"""
Dataset V2 preprocessing.

Creates train and test sets using complete simulation runs.
Rows from a test run never appear in training.
"""

import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler


DATASET_PATH = (
    "datasets/simulated/"
    "pneumatic_cylinder_dataset_v2.csv"
)

ROWS_PER_RUN = 400
TEST_RUN_COUNT = 5

# Only physical sensor/operating measurements
FEATURE_COLUMNS = [
    "Pressure",
    "Temperature",
    "Position",
    "Flow",
    "Speed",
    "Vibration",
    "Load",
]


def load_data():
    """Load Dataset V2 and assign its internal simulation RunID."""

    df = pd.read_csv(DATASET_PATH)

    required_columns = FEATURE_COLUMNS + ["Fault"]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    if len(df) % ROWS_PER_RUN != 0:
        raise ValueError(
            "Dataset rows are not divisible by ROWS_PER_RUN."
        )

    if df.isna().any().any():
        raise ValueError("Dataset contains missing values.")

    # Every 400 rows belong to one independent simulation
    df["RunID"] = (
        np.arange(len(df)) // ROWS_PER_RUN
    ) + 1

    print("=" * 60)
    print("DATASET V2 LOADED")
    print("=" * 60)
    print("Shape:", df.shape)
    print("Independent runs:", df["RunID"].nunique())

    return df


def identify_run_fault(fault_series):
    """
    Identify the planned fault for one simulation run.

    Faulty runs begin with healthy readings before the fault starts.
    Healthy-only runs contain no non-healthy label.
    """

    faulty_rows = fault_series[
        fault_series != "Healthy"
    ]

    if faulty_rows.empty:
        return "Healthy"

    return faulty_rows.mode().iloc[0]


def create_run_table(df):
    """Create one summary row for every simulation run."""

    run_table = (
        df.groupby("RunID")["Fault"]
        .apply(identify_run_fault)
        .reset_index(name="RunFault")
    )

    print("\nRuns by planned condition:")
    print(run_table["RunFault"].value_counts())

    return run_table


def preprocess_data(df):
    """
    Select one complete run from every condition for testing.

    Time, CycleCount and Health are intentionally excluded.
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
            "Run leakage detected between training and testing."
        )

    train_df = df[
        df["RunID"].isin(train_run_ids)
    ].copy()

    test_df = df[
        df["RunID"].isin(test_run_ids)
    ].copy()

    X_train = train_df[FEATURE_COLUMNS]
    X_test = test_df[FEATURE_COLUMNS]

    y_train_text = train_df["Fault"]
    y_test_text = test_df["Fault"]

    label_encoder = LabelEncoder()

    y_train = label_encoder.fit_transform(
        y_train_text
    )

    y_test = label_encoder.transform(
        y_test_text
    )

    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(
        X_train
    )

    X_test_scaled = scaler.transform(
        X_test
    )

    print("\n" + "=" * 60)
    print("LEAKAGE-FREE RUN SPLIT")
    print("=" * 60)

    print("Training runs:", train_run_ids)
    print("Testing runs :", test_run_ids)

    print("\nTesting run conditions:")
    print(
        test_runs[
            ["RunID", "RunFault"]
        ].sort_values("RunFault").to_string(
            index=False
        )
    )

    print("\nTraining samples:", len(X_train))
    print("Testing samples :", len(X_test))

    print("\nFeatures used:")
    for feature in FEATURE_COLUMNS:
        print("-", feature)

    print("\nFeatures excluded:")
    print("- Time")
    print("- CycleCount")
    print("- Health")
    print("- RunID")

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
    dataset = load_data()
    preprocess_data(dataset)