"""
Dataset Logger
Saves Digital Twin sensor data into CSV
"""

import csv
import os


class DatasetLogger:

    def __init__(self):

        self.file_path = "datasets/simulated/pneumatic_dataset.csv"

        os.makedirs("datasets/simulated", exist_ok=True)

        # Create CSV with Header
        if not os.path.exists(self.file_path):

            with open(self.file_path, "w", newline="") as file:

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
                    "Vibration"
                ])

    # ---------------------------------------
    # Save one sensor reading
    # ---------------------------------------
    def log(self, time_step, cylinder):

        with open(self.file_path, "a", newline="") as file:

            writer = csv.writer(file)

            writer.writerow([
                time_step,
                round(cylinder.pressure, 2),
                round(cylinder.temperature, 2),
                cylinder.position,
                round(cylinder.flow, 2),
                round(cylinder.speed, 2),
                cylinder.cycle_count,
                cylinder.health,
                cylinder.fault,
                round(cylinder.vibration, 2)
            ])