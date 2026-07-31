"""
Virtual Pneumatic Cylinder
"""

from backend.config.constants import *
from backend.simulator.sensors import VirtualSensors
from backend.simulator.faults import FaultEngine


class PneumaticCylinder:
    """
    Digital Twin representation of a Pneumatic Cylinder
    """

    def __init__(self):

        # Initial Sensor Values
        self.pressure = VirtualSensors.get_pressure()
        self.temperature = NORMAL_TEMPERATURE
        self.position = 0
        self.flow = VirtualSensors.get_flow()
        self.speed = VirtualSensors.get_speed()

        # Statistics
        self.cycle_count = 0
        self.health = MAX_HEALTH

        # Current Fault
        self.fault = HEALTHY

    # -------------------------------------
    # Update Virtual Sensors
    # -------------------------------------
    def update_sensors(self):

        self.pressure = VirtualSensors.get_pressure()

        self.temperature = VirtualSensors.get_temperature(
            self.temperature
        )

        self.flow = VirtualSensors.get_flow()

        self.speed = VirtualSensors.get_speed()

        # Apply Fault (if any)
        FaultEngine.apply_fault(self)

    # -------------------------------------
    # Move Forward
    # -------------------------------------
    def move_forward(self):

        if self.position < STROKE_LENGTH:

            self.position += 10

            if self.position > STROKE_LENGTH:
                self.position = STROKE_LENGTH

        self.cycle_count += 1

        self.update_sensors()

    # -------------------------------------
    # Move Backward
    # -------------------------------------
    def move_backward(self):

        if self.position > 0:

            self.position -= 10

            if self.position < 0:
                self.position = 0

        self.update_sensors()

    # -------------------------------------
    # Display Status
    # -------------------------------------
    def display_status(self):

        print("\n========== DIGITAL TWIN ==========")
        print(f"Pressure      : {self.pressure:.2f} bar")
        print(f"Temperature   : {self.temperature:.2f} °C")
        print(f"Position      : {self.position} mm")
        print(f"Flow          : {self.flow:.2f} L/min")
        print(f"Speed         : {self.speed:.2f} mm/s")
        print(f"Cycle Count   : {self.cycle_count}")
        print(f"Health Score  : {self.health}")
        print(f"Fault         : {self.fault}")
        print("==================================")