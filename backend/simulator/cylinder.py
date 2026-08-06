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

        # Load Sensor (Initialize first)
        self.load = NORMAL_LOAD

        # Initial Sensor Values
        self.pressure = VirtualSensors.get_pressure(self.load)
        self.temperature = NORMAL_TEMPERATURE
        self.position = 0
        self.flow = VirtualSensors.get_flow()
        self.speed = VirtualSensors.get_speed(self.load)

        # Vibration Sensor
        self.vibration = NORMAL_VIBRATION

        # Statistics
        self.cycle_count = 0
        self.health = MAX_HEALTH

        # Current Fault
        self.fault = HEALTHY

    # -------------------------------------
    # Update Virtual Sensors
    # -------------------------------------
    def update_sensors(self):

        # -------------------------------------
        # Load Simulation (Generate new load first)
        # -------------------------------------
        self.load = random.uniform(MIN_LOAD, MAX_LOAD)

        # Sensors affected by Load
        self.pressure = VirtualSensors.get_pressure(self.load)

        self.temperature = VirtualSensors.get_temperature(
            self.temperature
        )

        self.flow = VirtualSensors.get_flow()

        self.speed = VirtualSensors.get_speed(self.load)

        # Apply Fault (if any)
        FaultEngine.apply_fault(self)

        # -------------------------------------
        # Vibration Simulation
        # -------------------------------------
        if self.fault == HEALTHY:
            self.vibration = random.uniform(0.2, 0.6)

        elif self.fault == AIR_LEAKAGE:
            self.vibration = random.uniform(0.8, 1.2)

        elif self.fault == SEAL_WEAR:
            self.vibration = random.uniform(1.5, 2.5)

        elif self.fault == VALVE_STICKING:
            self.vibration = random.uniform(2.5, 4.0)

        elif self.fault == PRESSURE_DROP:
            self.vibration = random.uniform(1.0, 2.0)

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
        print(f"Health Score  : {self.health}")
        print(f"Fault         : {self.fault}")
        print("==================================")