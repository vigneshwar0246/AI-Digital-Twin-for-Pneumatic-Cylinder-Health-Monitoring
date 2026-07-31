"""
Dataset Logger
Saves every simulation step into a CSV file.
"""

import csv
import os


class DatasetLogger:

    def __init__(self):

        # Folder to store generated datasets
        self.dataset_folder = "datasets/simulated"

        # Dataset filename
        self.dataset_file = os.path.join(
            self.dataset_folder,
            "pneumatic_dataset.csv"
        )

        # Create folder if it doesn't exist
        os.makedirs(self.dataset_folder, exist_ok=True)

        # Create CSV file with header if it doesn't exist
        if not os.path.exists(self.dataset_file):

            with open(self.dataset_file, "w", newline="") as file:

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
                    "Fault"
                ])

    def log(self, time_step, cylinder):

        with open(self.dataset_file, "a", newline="") as file:

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
                cylinder.fault
            ])