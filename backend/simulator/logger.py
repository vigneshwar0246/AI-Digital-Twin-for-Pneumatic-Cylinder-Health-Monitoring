"""
Dataset Logger + Dataset Generator
"""

import csv
import os

OUTPUT_FILE = "datasets/simulated/pneumatic_cylinder_dataset.csv"


class DatasetLogger:
    """
    Logs one row of sensor data into the CSV file.
    """

    def __init__(self):

        os.makedirs("datasets/simulated", exist_ok=True)

        self.file = open(OUTPUT_FILE, "w", newline="")

        self.writer = csv.writer(self.file)

        self.writer.writerow([
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

    def log(self, time_step, cylinder):

        self.writer.writerow([
            time_step,
            round(cylinder.pressure, 2),
            round(cylinder.temperature, 2),
            cylinder.position,
            round(cylinder.flow, 2),
            round(cylinder.speed, 2),
            cylinder.cycle_count,
            cylinder.health,
            cylinder.fault,
            round(cylinder.vibration, 2),
            round(cylinder.load, 2)
        ])

        self.file.flush()

    def close(self):
        self.file.close()