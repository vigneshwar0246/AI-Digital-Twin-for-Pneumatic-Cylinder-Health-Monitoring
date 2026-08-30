"""
Dataset V2.1 generator.

Creates 20,000 rows from 50 independent runs:
10 runs for each planned operating condition.

The main dataset retains the original 11-column format.
Simulation metadata is stored separately.
"""

import csv
import os
import random

from collections import Counter

from backend.config.constants import HEALTHY

from backend.simulator.cylinder_v2_1 import (
    PneumaticCylinderV21,
)

from backend.simulator.faults_v2_1 import (
    FaultEngineV21,
)


OUTPUT_FILE = (
    "datasets/simulated/"
    "pneumatic_cylinder_dataset_v2_1.csv"
)

METADATA_FILE = (
    "datasets/simulated/"
    "pneumatic_cylinder_dataset_v2_1_metadata.csv"
)

RUNS_PER_CONDITION = 10
ROWS_PER_RUN = 400

TOTAL_RUNS = (
    len(FaultEngineV21.FAULT_TYPES)
    * RUNS_PER_CONDITION
)

TOTAL_ROWS = TOTAL_RUNS * ROWS_PER_RUN

RANDOM_SEED = 84

SEVERITY_LEVELS = [
    0.40,
    0.55,
    0.70,
    0.85,
    1.00,
]


def create_run_schedule():
    """
    Create ten runs per condition.

    Every faulty condition receives each severity level
    exactly twice, preventing severity imbalance.
    """

    schedule = []

    for planned_fault in FaultEngineV21.FAULT_TYPES:

        if planned_fault == HEALTHY:

            for _ in range(RUNS_PER_CONDITION):
                schedule.append({
                    "planned_fault": HEALTHY,
                    "maximum_severity": 0.0,
                })

        else:

            severity_schedule = (
                SEVERITY_LEVELS * 2
            )

            random.shuffle(severity_schedule)

            for severity in severity_schedule:
                schedule.append({
                    "planned_fault": planned_fault,
                    "maximum_severity": severity,
                })

    random.shuffle(schedule)

    return schedule


def generate_dataset_v2_1():

    random.seed(RANDOM_SEED)

    os.makedirs(
        "datasets/simulated",
        exist_ok=True,
    )

    schedule = create_run_schedule()

    planned_run_counts = Counter()
    observed_fault_counts = Counter()

    valve_event_rows = 0
    global_time = 0

    with (
        open(
            OUTPUT_FILE,
            "w",
            newline="",
            encoding="utf-8",
        ) as dataset_file,
        open(
            METADATA_FILE,
            "w",
            newline="",
            encoding="utf-8",
        ) as metadata_file,
    ):

        dataset_writer = csv.writer(
            dataset_file
        )

        metadata_writer = csv.writer(
            metadata_file
        )

        dataset_writer.writerow([
            "Time",
            "Pressure",
            "Temperature",
            "Position",
            "Flow",
            "Speed",
            "CycleCount",
            "Health",
            "Fault",
            "Vibration",
            "Load",
        ])

        metadata_writer.writerow([
            "Time",
            "RunID",
            "Step",
            "PlannedFault",
            "ObservedFault",
            "Severity",
            "FaultStart",
            "RiseTime",
            "MaximumSeverity",
            "Direction",
            "LoadPhase",
            "ValveEvent",
        ])

        for run_id, run_config in enumerate(
            schedule,
            start=1,
        ):

            planned_fault = run_config[
                "planned_fault"
            ]

            maximum_severity = run_config[
                "maximum_severity"
            ]

            planned_run_counts[
                planned_fault
            ] += 1

            if planned_fault == HEALTHY:
                fault_start = None
                rise_time = 1

            else:
                fault_start = random.randint(
                    35,
                    70,
                )

                rise_time = random.randint(
                    60,
                    120,
                )

            cylinder = PneumaticCylinderV21(
                planned_fault=planned_fault,
                fault_start=fault_start,
                maximum_severity=maximum_severity,
                rise_time=rise_time,
            )

            for step_number in range(
                ROWS_PER_RUN
            ):

                global_time += 1

                cylinder.simulate_step(
                    step_number
                )

                state = cylinder.get_state()
                metadata = cylinder.get_metadata()

                observed_fault_counts[
                    state["Fault"]
                ] += 1

                valve_event_rows += metadata[
                    "ValveEvent"
                ]

                dataset_writer.writerow([
                    global_time,
                    state["Pressure"],
                    state["Temperature"],
                    state["Position"],
                    state["Flow"],
                    state["Speed"],
                    state["CycleCount"],
                    state["Health"],
                    state["Fault"],
                    state["Vibration"],
                    state["Load"],
                ])

                metadata_writer.writerow([
                    global_time,
                    run_id,
                    step_number,
                    metadata["PlannedFault"],
                    state["Fault"],
                    metadata["Severity"],
                    (
                        fault_start
                        if fault_start is not None
                        else ""
                    ),
                    rise_time,
                    maximum_severity,
                    metadata["Direction"],
                    metadata["LoadPhase"],
                    metadata["ValveEvent"],
                ])

    print("\n" + "=" * 52)
    print("DATASET V2.1 GENERATED SUCCESSFULLY")
    print("=" * 52)

    print(f"Independent Runs : {TOTAL_RUNS}")
    print(f"Rows Per Run     : {ROWS_PER_RUN}")
    print(f"Total Rows       : {TOTAL_ROWS}")

    print("\nPlanned Runs:")

    for fault in FaultEngineV21.FAULT_TYPES:
        print(
            f"{fault:<18}: "
            f"{planned_run_counts[fault]}"
        )

    print("\nObserved Row Distribution:")

    for fault, count in (
        observed_fault_counts.items()
    ):
        percentage = (
            count / TOTAL_ROWS
        ) * 100

        print(
            f"{fault:<18}: "
            f"{count:>5} "
            f"({percentage:.2f}%)"
        )

    print(
        f"\nValve Event Rows : "
        f"{valve_event_rows}"
    )

    print(f"\nDataset : {OUTPUT_FILE}")
    print(f"Metadata: {METADATA_FILE}")

    print("=" * 52)


if __name__ == "__main__":
    generate_dataset_v2_1()