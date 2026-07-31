"""
Dataset Generator
Generates a large AI training dataset automatically.
"""

from backend.simulator.cylinder import PneumaticCylinder
from backend.simulator.logger import DatasetLogger


class DatasetGenerator:

    def __init__(self):

        self.cylinder = PneumaticCylinder()

        self.logger = DatasetLogger()

        self.time_step = 0

    def generate(self, total_rows=10000):

        print("\nGenerating Dataset...\n")

        while self.time_step < total_rows:

            # -------------------------
            # Move Forward
            # -------------------------
            while self.cylinder.position < 100 and self.time_step < total_rows:

                self.cylinder.move_forward()

                self.time_step += 1

                self.logger.log(self.time_step, self.cylinder)

            # -------------------------
            # Move Backward
            # -------------------------
            while self.cylinder.position > 0 and self.time_step < total_rows:

                self.cylinder.move_backward()

                self.time_step += 1

                self.logger.log(self.time_step, self.cylinder)

        print(f"\nDataset Generated Successfully!")
        print(f"Rows Generated : {self.time_step}")


if __name__ == "__main__":

    generator = DatasetGenerator()

    generator.generate(total_rows=10000)