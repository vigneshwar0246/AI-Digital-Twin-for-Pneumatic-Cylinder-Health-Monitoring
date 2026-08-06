"""
Dataset Generator
Generates exactly 10,000 rows from the Digital Twin
"""

import csv
import os

from backend.simulator.cylinder import PneumaticCylinder

OUTPUT_FILE = "datasets/simulated/pneumatic_cylinder_dataset.csv"


def generate_dataset(rows=10000):

    os.makedirs("datasets/simulated", exist_ok=True)

    cylinder = PneumaticCylinder()

    with open(OUTPUT_FILE, "w", newline="") as file:

        writer = csv.writer(file)

        # Header
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

        for t in range(1, rows + 1):

            if cylinder.position >= 100:
                cylinder.move_backward()
            else:
                cylinder.move_forward()

            writer.writerow([
                t,
                round(cylinder.pressure, 2),
                round(cylinder.temperature, 2),
                cylinder.position,
                round(cylinder.flow, 2),
                round(cylinder.speed, 2),
                cylinder.cycle_count,
                round(cylinder.health, 2),
                cylinder.fault,
                round(cylinder.vibration, 2),
                round(cylinder.load, 2)
            ])

    print("\n===================================")
    print("Dataset Generated Successfully!")
    print(f"Rows Generated : {rows}")
    print(f"Saved To : {OUTPUT_FILE}")
    print("===================================")


if __name__ == "__main__":
    generate_dataset(10000)