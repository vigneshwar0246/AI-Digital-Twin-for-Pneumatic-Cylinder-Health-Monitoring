
"""
Realistic Pneumatic Cylinder for Dataset V2
"""

import random

from backend.config.constants import (
    STROKE_LENGTH,
    NORMAL_TEMPERATURE,
    NORMAL_LOAD,
    MIN_LOAD,
    MAX_LOAD,
    MAX_HEALTH,
    HEALTHY,
    AIR_LEAKAGE,
    PRESSURE_DROP,
    SEAL_WEAR,
    VALVE_STICKING
)

from backend.simulator.faults_v2 import FaultEngineV2


class PneumaticCylinderV2:
    """
    Pneumatic-cylinder simulation with:

    - Complete forward and backward movement
    - Stable operating load with gradual variation
    - Independent fault episodes
    - Gradual fault severity
    - Overlapping sensor ranges
    """

    def __init__(
        self,
        run_fault=HEALTHY,
        fault_start=None,
        maximum_severity=0.8,
        rise_time=80
    ):

        self.run_fault = run_fault
        self.fault_start = fault_start
        self.maximum_severity = maximum_severity
        self.rise_time = rise_time

        self.position = 0
        self.direction = 1
        self.cycle_count = 0

        self.load_target = random.uniform(MIN_LOAD, MAX_LOAD)
        self.load = NORMAL_LOAD

        self.pressure = 5.5
        self.temperature = NORMAL_TEMPERATURE
        self.flow = 10.0
        self.speed = 120.0
        self.vibration = 0.4

        self.health = MAX_HEALTH
        self.fault = HEALTHY
        self.severity = 0.0

    @staticmethod
    def clamp(value, minimum, maximum):
        return max(minimum, min(maximum, value))

    def update_position(self):
        """
        Completes the full extension and retraction stroke.
        One cycle is counted after returning to 0 mm.
        """

        self.position += self.direction * 10

        if self.position >= STROKE_LENGTH:
            self.position = STROKE_LENGTH
            self.direction = -1

        elif self.position <= 0:
            self.position = 0
            self.direction = 1
            self.cycle_count += 1

    def update_health(self):
        """
        Gradually degrades health according to fault severity.
        """

        if self.fault == HEALTHY:
            degradation = random.uniform(0.000, 0.005)

        elif self.fault == AIR_LEAKAGE:
            degradation = random.uniform(0.05, 0.12) * self.severity

        elif self.fault == PRESSURE_DROP:
            degradation = random.uniform(0.07, 0.15) * self.severity

        elif self.fault == SEAL_WEAR:
            degradation = random.uniform(0.08, 0.18) * self.severity

        elif self.fault == VALVE_STICKING:
            degradation = random.uniform(0.10, 0.22) * self.severity

        else:
            degradation = 0

        self.health = self.clamp(
            self.health - degradation,
            0,
            MAX_HEALTH
        )

    def update_sensors(self, step_number):
        """
        Generates normal sensor readings and then applies
        the selected gradual fault condition.
        """

        # Load changes gradually around one operating target
        self.load += (
            (self.load_target - self.load) * 0.08
            + random.uniform(-0.70, 0.70)
        )

        self.load = self.clamp(
            self.load,
            MIN_LOAD,
            MAX_LOAD
        )

        values = {
            "pressure": (
                4.9
                + (self.load / MAX_LOAD) * 1.0
                + random.uniform(-0.12, 0.12)
            ),

            "flow": (
                10.0
                + random.uniform(-0.35, 0.35)
            ),

            "speed": (
                129
                - (self.load / MAX_LOAD) * 14
                + random.uniform(-2.5, 2.5)
            ),

            "temperature_target": (
                30
                + (self.load / MAX_LOAD) * 5
                + random.uniform(-1.0, 1.0)
            ),

            "vibration": (
                0.30
                + (self.load / MAX_LOAD) * 0.25
                + random.uniform(-0.12, 0.12)
            )
        }

        if (
            self.run_fault != HEALTHY
            and self.fault_start is not None
            and step_number >= self.fault_start
        ):
            self.fault = self.run_fault

            self.severity = FaultEngineV2.calculate_severity(
                step_number,
                self.fault_start,
                self.rise_time,
                self.maximum_severity
            )

        else:
            self.fault = HEALTHY
            self.severity = 0.0

        values = FaultEngineV2.apply_fault(
            values,
            self.fault,
            self.severity
        )

        # Temperature changes gradually
        self.temperature += (
            values["temperature_target"] - self.temperature
        ) * random.uniform(0.08, 0.18)

        # Physical sensor boundaries include abnormal conditions
        self.pressure = self.clamp(
            values["pressure"], 3.5, 6.2
        )

        self.flow = self.clamp(
            values["flow"], 7.5, 12.5
        )

        self.speed = self.clamp(
            values["speed"], 85, 132
        )

        self.temperature = self.clamp(
            self.temperature, 25, 65
        )

        self.vibration = self.clamp(
            values["vibration"], 0.1, 4.5
        )

        self.update_health()

    def simulate_step(self, step_number):
        self.update_position()
        self.update_sensors(step_number)

    def get_state(self):
        return {
            "Pressure": round(self.pressure, 2),
            "Temperature": round(self.temperature, 2),
            "Position": self.position,
            "Flow": round(self.flow, 2),
            "Speed": round(self.speed, 2),
            "CycleCount": self.cycle_count,
            "Health": round(self.health, 2),
            "Fault": self.fault,
            "Vibration": round(self.vibration, 2),
            "Load": round(self.load, 2)
        }