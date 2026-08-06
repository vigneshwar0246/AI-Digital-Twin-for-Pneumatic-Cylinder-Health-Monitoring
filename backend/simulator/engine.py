"""
Digital Twin Simulation Engine
Generates exactly 10,000 synthetic sensor readings
"""

import time

from backend.simulator.cylinder import PneumaticCylinder
from backend.simulator.logger import DatasetLogger


TOTAL_ROWS = 10000


def run_simulation():

    cylinder = PneumaticCylinder()

    logger = DatasetLogger()

    time_step = 0

    print("\nGenerating Dataset...\n")

    while time_step < TOTAL_ROWS:

        # -------------------------
        # Move Forward
        # -------------------------
        while cylinder.position < 100 and time_step < TOTAL_ROWS:

            cylinder.move_forward()

            time_step += 1

            logger.log(time_step, cylinder)

        # -------------------------
        # Move Backward
        # -------------------------
        while cylinder.position > 0 and time_step < TOTAL_ROWS:

            cylinder.move_backward()

            time_step += 1

            logger.log(time_step, cylinder)

    logger.close()

    print("\n===================================")
    print("Dataset Generated Successfully!")
    print(f"Rows Generated : {time_step}")
    print("Saved To : datasets/simulated/pneumatic_cylinder_dataset.csv")
    print("===================================")


if __name__ == "__main__":
    run_simulation()