"""
Digital Twin Simulation Engine
"""

import time

from backend.simulator.cylinder import PneumaticCylinder
from backend.simulator.logger import DatasetLogger


def run_simulation():

    cylinder = PneumaticCylinder()

    logger = DatasetLogger()

    time_step = 0

    print("\nStarting Digital Twin Simulation...\n")

    while True:

        # -------------------------
        # Move Forward
        # -------------------------

        while cylinder.position < 100:

            cylinder.move_forward()

            cylinder.display_status()

            time_step += 1

            logger.log(time_step, cylinder)

            time.sleep(1)

        # -------------------------
        # Move Backward
        # -------------------------

        while cylinder.position > 0:

            cylinder.move_backward()

            cylinder.display_status()

            time_step += 1

            logger.log(time_step, cylinder)

            time.sleep(1)


if __name__ == "__main__":
    run_simulation()