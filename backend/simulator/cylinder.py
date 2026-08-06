"""
Virtual Pneumatic Cylinder
"""

import random

from backend.config.constants import *
from backend.simulator.sensors import VirtualSensors
from backend.simulator.faults import FaultEngine


class PneumaticCylinder:
    """
    Digital Twin representation of a Pneumatic Cylinder
    """

    def __init__(self):

        # -------------------------------------
        # Load Sensor
        # -------------------------------------

        self.load = NORMAL_LOAD

        # -------------------------------------
        # Initial Sensor Values
        # -------------------------------------

        self.pressure = VirtualSensors.get_pressure(self.load)

        self.temperature = NORMAL_TEMPERATURE

        self.position = 0

        self.flow = VirtualSensors.get_flow()

        self.speed = VirtualSensors.get_speed(self.load)

        self.vibration = NORMAL_VIBRATION

        # -------------------------------------
        # Statistics
        # -------------------------------------

        self.cycle_count = 0

        self.health = MAX_HEALTH

        # -------------------------------------
        # Current Fault
        # -------------------------------------

        self.fault = HEALTHY

    # -------------------------------------
    # Update Virtual Sensors
    # -------------------------------------

    def update_sensors(self):

        # Random load for every cycle
        self.load = round(
            random.uniform(
                MIN_LOAD,
                MAX_LOAD
            ),
            2
        )

        # Pressure depends on load
        self.pressure = VirtualSensors.get_pressure(
            self.load
        )

        # Flow
        self.flow = VirtualSensors.get_flow()

        # Speed depends on load
        self.speed = VirtualSensors.get_speed(
            self.load
        )

        # Apply faults first
        FaultEngine.apply_fault(self)

        # Temperature depends on current fault
        self.temperature = VirtualSensors.get_temperature(
            self.temperature,
            self.fault
        )

        # -------------------------------------
        # Vibration
        # -------------------------------------

        if self.fault == HEALTHY:

            self.vibration = round(
                random.uniform(0.2, 0.6),
                2
            )

        elif self.fault == AIR_LEAKAGE:

            self.vibration = round(
                random.uniform(0.8, 1.2),
                2
            )

        elif self.fault == SEAL_WEAR:

            self.vibration = round(
                random.uniform(1.5, 2.5),
                2
            )

        elif self.fault == VALVE_STICKING:

            self.vibration = round(
                random.uniform(2.5, 4.0),
                2
            )

        elif self.fault == PRESSURE_DROP:

            self.vibration = round(
                random.uniform(1.0, 2.0),
                2
            )

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
        print(f"Vibration     : {self.vibration:.2f} mm/s")
        print(f"Load          : {self.load:.2f} kg")
        print(f"Cycle Count   : {self.cycle_count}")
        print(f"Health Score  : {self.health:.2f}")
        print(f"Fault         : {self.fault}")
        print("==================================")