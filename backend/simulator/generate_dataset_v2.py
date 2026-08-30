"""
Dataset V2 Generator

Generates exactly 10,000 rows from 25 independent
pneumatic-cylinder simulation runs.

Dataset V1 is not modified.
"""

import csv
import os
import random

from collections import Counter

from backend.config.constants import HEALTHY
from backend.simulator.cylinder_v2 import PneumaticCylinderV2
from backend.simulator.faults_v2 import FaultEngineV2


OUTPUT_FILE = (
    "datasets/simulated/"
    "pneumatic_cylinder_dataset_v2.csv"
)

TOTAL_RUNS = 25
ROWS_PER_RUN = 400
TOTAL_ROWS = TOTAL_RUNS * ROWS_PER_RUN

RANDOM_SEED = 42


def create_fault_schedule():
    """
    Creates five independent runs for each fault condition.

    The schedule is shuffled so faults are not connected
    to a fixed Time or CycleCount range.
    """

    schedule = FaultEngineV2.FAULT_TYPES * 5

    random.shuffle(schedule)

    return schedule


def generate_dataset_v2():

    random.seed(RANDOM_SEED)

    os.makedirs(
        "datasets/simulated",
        exist_ok=True
    )

    fault_schedule = create_fault_schedule()

    fault_counts = Counter()

    global_time = 0

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
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
            "Load"
        ])

        for run_number, run_fault in enumerate(
            fault_schedule,
            start=1
        ):

            if run_fault == HEALTHY:

                fault_start = None
                maximum_severity = 0.0
                rise_time = 1

            else:

                # Different onset for every independent run
                fault_start = random.randint(40, 80)

                # Mild, moderate or severe fault
                maximum_severity = random.choice([
                    0.45,
                    0.70,
                    0.95
                ])

                # Different fault-development speed
                rise_time = random.randint(50, 120)

            cylinder = PneumaticCylinderV2(
                run_fault=run_fault,
                fault_start=fault_start,
                maximum_severity=maximum_severity,
                rise_time=rise_time
            )

            for step_number in range(ROWS_PER_RUN):

                global_time += 1

                cylinder.simulate_step(step_number)

                state = cylinder.get_state()

                fault_counts[state["Fault"]] += 1

                writer.writerow([
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
                    state["Load"]
                ])

    print("\n==========================================")
    print("Dataset V2 Generated Successfully!")
    print(f"Independent Runs : {TOTAL_RUNS}")
    print(f"Rows Per Run     : {ROWS_PER_RUN}")
    print(f"Total Rows       : {TOTAL_ROWS}")
    print(f"Saved To         : {OUTPUT_FILE}")

    print("\nFault Distribution:")

    for fault, count in fault_counts.items():
        percentage = (count / TOTAL_ROWS) * 100

        print(
            f"{fault:<18}: "
            f"{count:>4} "
            f"({percentage:.2f}%)"
        )

    print("==========================================")


if __name__ == "__main__":
    generate_dataset_v2()