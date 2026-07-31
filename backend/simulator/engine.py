"""
Digital Twin Simulation Engine
"""

import time

from backend.simulator.cylinder import PneumaticCylinder


def run_simulation():

    cylinder = PneumaticCylinder()

    print("\nStarting Digital Twin Simulation...\n")

    while True:

        # Move Forward
        while cylinder.position < 100:

            cylinder.move_forward()

            cylinder.display_status()

            time.sleep(1)

        # Move Backward
        while cylinder.position > 0:

            cylinder.move_backward()

            cylinder.display_status()

            time.sleep(1)


if __name__ == "__main__":
    run_simulation()