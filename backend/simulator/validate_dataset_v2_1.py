"""
Structural validation for Dataset V2.1.
"""

import pandas as pd


DATASET_PATH = (
    "datasets/simulated/"
    "pneumatic_cylinder_dataset_v2_1.csv"
)

METADATA_PATH = (
    "datasets/simulated/"
    "pneumatic_cylinder_dataset_v2_1_metadata.csv"
)

EXPECTED_ROWS = 20000
EXPECTED_RUNS = 50
ROWS_PER_RUN = 400

EXPECTED_POSITIONS = set(
    range(0, 101, 10)
)

EXPECTED_RUN_COUNTS = {
    "Healthy": 10,
    "Air Leakage": 10,
    "Pressure Drop": 10,
    "Seal Wear": 10,
    "Valve Sticking": 10,
}


def validate():

    dataset = pd.read_csv(DATASET_PATH)
    metadata = pd.read_csv(METADATA_PATH)

    merged = dataset.merge(
        metadata,
        on="Time",
        validate="one_to_one",
    )

    metadata_required = [
        "Time",
        "RunID",
        "Step",
        "PlannedFault",
        "ObservedFault",
        "Severity",
        "RiseTime",
        "MaximumSeverity",
        "Direction",
        "LoadPhase",
        "ValveEvent",
    ]

    run_sizes = metadata.groupby(
        "RunID"
    ).size()

    run_conditions = (
        metadata.groupby("RunID")[
            "PlannedFault"
        ].first().value_counts().to_dict()
    )

    stroke_coverage = merged.groupby(
        "RunID"
    )["Position"].agg(["min", "max"])

    detectable_rows = (
        merged["ObservedFault"] != "Healthy"
    )

    checks = {
        "Dataset has 20,000 rows":
            len(dataset) == EXPECTED_ROWS,

        "Metadata has 20,000 rows":
            len(metadata) == EXPECTED_ROWS,

        "Dataset has 11 columns":
            len(dataset.columns) == 11,

        "Metadata has 12 columns":
            len(metadata.columns) == 12,

        "Dataset has no missing values":
            not dataset.isna().any().any(),

        "Required metadata has no missing values":
            not metadata[
                metadata_required
            ].isna().any().any(),

        "Dataset has no duplicate timestamps":
            not dataset["Time"].duplicated().any(),

        "Metadata has no duplicate timestamps":
            not metadata["Time"].duplicated().any(),

        "Time is continuous":
            dataset["Time"].tolist()
            == list(range(1, EXPECTED_ROWS + 1)),

        "Dataset and metadata times align":
            dataset["Time"].equals(
                metadata["Time"]
            ),

        "Exactly 50 independent runs":
            metadata["RunID"].nunique()
            == EXPECTED_RUNS,

        "Every run has 400 rows":
            run_sizes.eq(
                ROWS_PER_RUN
            ).all(),

        "Every condition has 10 runs":
            run_conditions
            == EXPECTED_RUN_COUNTS,

        "Planned fault is constant within each run":
            metadata.groupby("RunID")[
                "PlannedFault"
            ].nunique().eq(1).all(),

        "All runs contain five load phases":
            metadata.groupby("RunID")[
                "LoadPhase"
            ].nunique().eq(5).all(),

        "Position values are valid":
            set(dataset["Position"].unique())
            == EXPECTED_POSITIONS,

        "Every run reaches 0 and 100 mm":
            (
                stroke_coverage["min"].eq(0)
                & stroke_coverage["max"].eq(100)
            ).all(),

        "Dataset and metadata labels align":
            merged["Fault"].equals(
                merged["ObservedFault"]
            ),

        "Detectable labels meet severity threshold":
            merged.loc[
                detectable_rows,
                "Severity"
            ].ge(0.15).all(),

        "Detected faults match planned faults":
            merged.loc[
                detectable_rows,
                "ObservedFault"
            ].equals(
                merged.loc[
                    detectable_rows,
                    "PlannedFault"
                ]
            ),

        "Sub-threshold rows remain Healthy":
            merged.loc[
                merged["Severity"] < 0.15,
                "ObservedFault"
            ].eq("Healthy").all(),

        "Valve events occur only in valve runs":
            merged.loc[
                merged["ValveEvent"] == 1,
                "PlannedFault"
            ].eq("Valve Sticking").all(),
    }

    print("=" * 64)
    print("DATASET V2.1 VALIDATION")
    print("=" * 64)

    for check_name, passed in checks.items():
        result = "PASS" if passed else "FAIL"
        print(f"{result:<5} | {check_name}")

    print("\nObserved fault distribution:")
    print(dataset["Fault"].value_counts())

    print("\nSensor boundaries:")
    print(
        dataset[[
            "Pressure",
            "Temperature",
            "Flow",
            "Speed",
            "Vibration",
            "Load",
            "Health",
        ]].agg(["min", "max"]).round(2)
    )

    load_span = merged.groupby(
        "RunID"
    )["Load"].agg(
        lambda values:
        values.max() - values.min()
    )

    print(
        "\nMinimum load range within any run:",
        round(load_span.min(), 2),
        "kg",
    )

    print(
        "Valve-event rows:",
        int(metadata["ValveEvent"].sum()),
    )

    if not all(checks.values()):
        raise ValueError(
            "Dataset V2.1 validation failed."
        )

    print("\nAll Dataset V2.1 checks passed.")


if __name__ == "__main__":
    validate()