"""
Dataset Logger
Saves every simulation step into a CSV file.
"""

import csv
import os


class DatasetLogger:
    """Persist Digital Twin sensor/state data as CSV."""

    HEADER = [
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
    ]

    def __init__(self, dataset_file="datasets/simulated/pneumatic_cylinder_dataset.csv", reset=False):
        self.dataset_file = dataset_file
        os.makedirs(os.path.dirname(self.dataset_file), exist_ok=True)

        if reset or not os.path.exists(self.dataset_file):
            self._write_header()

    def _write_header(self):
        with open(self.dataset_file, "w", newline="", encoding="utf-8") as file:
            csv.writer(file).writerow(self.HEADER)

    def log(self, time_step, cylinder):
        """Append one simulation observation."""
        with open(self.dataset_file, "a", newline="", encoding="utf-8") as file:
            csv.writer(file).writerow([
                time_step,
                round(cylinder.pressure, 2),
                round(cylinder.temperature, 2),
                cylinder.position,
                round(cylinder.flow, 2),
                round(cylinder.speed, 2),
                cylinder.cycle_count,
                round(cylinder.health, 2),
                cylinder.fault,
                round(cylinder.vibration, 2),
                round(cylinder.load, 2),
            ])
