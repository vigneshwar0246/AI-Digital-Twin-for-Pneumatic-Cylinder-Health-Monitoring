"""
Digital Twin Simulation Engine
Live Simulation + Continuous Dataset Logging
"""

import time
import os
import pandas as pd

from backend.simulator.cylinder import PneumaticCylinder
from backend.simulator.logger import DatasetLogger


OUTPUT_FILE = "datasets/simulated/pneumatic_cylinder_dataset.csv"


def get_last_time_step():

    if not os.path.exists(OUTPUT_FILE):
        return 0

    try:

        df = pd.read_csv(OUTPUT_FILE)

        if len(df) == 0:
            return 0

        return int(df["Time"].iloc[-1])

    except Exception:
        return 0


def run_simulation():

    cylinder = PneumaticCylinder()

    logger = DatasetLogger()

    time_step = get_last_time_step()

    print("\nStarting Digital Twin Simulation...\n")

    try:

        while True:

            while cylinder.position < 100:

                cylinder.move_forward()

                cylinder.display_status()

                time_step += 1

                logger.log(time_step, cylinder)

                time.sleep(1)

            while cylinder.position > 0:

                cylinder.move_backward()

                cylinder.display_status()

                time_step += 1

                logger.log(time_step, cylinder)

                time.sleep(1)

    except KeyboardInterrupt:

        print("\n\nSimulation Stopped by User.")

        print(f"\nDataset updated successfully.")
        print(f"Total Rows : {time_step}")
        print(f"Location : {OUTPUT_FILE}")


if __name__ == "__main__":
    run_simulation()