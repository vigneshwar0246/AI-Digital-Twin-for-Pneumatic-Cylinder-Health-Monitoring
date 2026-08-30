"""
Stateful pneumatic-cylinder simulator for Dataset V2.1.
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
    VALVE_STICKING,
)

from backend.simulator.faults_v2_1 import (
    FaultEngineV21,
)


class PneumaticCylinderV21:
    """
    V2.1 improvements:

    - Multiple load conditions inside every run
    - Complete forward/backward movement
    - Smooth fault development
    - Detectable fault-labelling threshold
    - Multi-step valve-sticking events
    - Actual position pauses during valve sticking
    """

    LOAD_PHASE_LENGTH = 80

    def __init__(
        self,
        planned_fault=HEALTHY,
        fault_start=None,
        maximum_severity=0.8,
        rise_time=80,
    ):
        self.planned_fault = planned_fault
        self.fault_start = fault_start
        self.maximum_severity = maximum_severity
        self.rise_time = rise_time

        self.position = 0
        self.direction = 1
        self.cycle_count = 0

        # Every run experiences low, medium and high loads.
        self.load_targets = [
            random.uniform(7, 16),
            random.uniform(18, 28),
            random.uniform(30, 39),
            random.uniform(41, 49),
            random.uniform(MIN_LOAD, MAX_LOAD),
        ]

        random.shuffle(self.load_targets)

        self.load_phase_index = 0
        self.load_target = self.load_targets[0]
        self.load = NORMAL_LOAD

        self.pressure = 5.5
        self.temperature = NORMAL_TEMPERATURE
        self.flow = 10.0
        self.speed = 120.0
        self.vibration = 0.4

        self.health = MAX_HEALTH
        self.fault = HEALTHY
        self.severity = 0.0

        # Stateful valve-sticking event
        self.valve_event_steps = 0
        self.valve_event_active = False

    @staticmethod
    def clamp(value, minimum, maximum):
        return max(
            minimum,
            min(maximum, value),
        )

    def update_position(self):
        """
        Complete the forward/backward stroke.

        During a valve-sticking event, movement may pause,
        creating a measurable temporal position irregularity.
        """

        movement_blocked = (
            self.valve_event_steps > 0
            and random.random() < 0.75
        )

        if movement_blocked:
            return

        self.position += self.direction * 10

        if self.position >= STROKE_LENGTH:
            self.position = STROKE_LENGTH
            self.direction = -1

        elif self.position <= 0:
            self.position = 0
            self.direction = 1
            self.cycle_count += 1

    def update_load(self, step_number):
        """
        Move through five operating-load phases so Load
        cannot behave like a simulation-run identifier.
        """

        if (
            step_number > 0
            and step_number % self.LOAD_PHASE_LENGTH == 0
        ):
            self.load_phase_index = (
                self.load_phase_index + 1
            ) % len(self.load_targets)

            self.load_target = self.load_targets[
                self.load_phase_index
            ]

        self.load += (
            (self.load_target - self.load) * 0.10
            + random.uniform(-0.65, 0.65)
        )

        self.load = self.clamp(
            self.load,
            MIN_LOAD,
            MAX_LOAD,
        )

    def update_fault_state(self, step_number):
        """Update physical severity and observable label."""

        if (
            self.planned_fault == HEALTHY
            or self.fault_start is None
            or step_number < self.fault_start
        ):
            self.severity = 0.0
            self.fault = HEALTHY
            return

        self.severity = FaultEngineV21.calculate_severity(
            step_number,
            self.fault_start,
            self.rise_time,
            self.maximum_severity,
        )

        self.fault = FaultEngineV21.detectable_label(
            self.planned_fault,
            self.severity,
        )

    def update_valve_event(self, values):
        """
        Start and maintain intermittent valve-sticking events.

        Event probability increases with fault severity.
        """

        self.valve_event_active = False

        if (
            self.planned_fault != VALVE_STICKING
            or self.severity
            < FaultEngineV21.DETECTION_THRESHOLD
        ):
            self.valve_event_steps = 0
            return values

        if self.valve_event_steps == 0:
            event_probability = (
                0.03
                + 0.15 * self.severity
            )

            if random.random() < event_probability:
                self.valve_event_steps = random.randint(
                    3,
                    8,
                )

        if self.valve_event_steps > 0:
            self.valve_event_active = True

            values = FaultEngineV21.apply_valve_event(
                values,
                self.severity,
            )

            self.valve_event_steps -= 1

        return values

    def update_health(self):
        """Degrade health from the underlying physical fault."""

        if (
            self.planned_fault == HEALTHY
            or self.severity <= 0
        ):
            degradation = random.uniform(
                0.000,
                0.004,
            )

        elif self.planned_fault == AIR_LEAKAGE:
            degradation = (
                random.uniform(0.04, 0.10)
                * self.severity
            )

        elif self.planned_fault == PRESSURE_DROP:
            degradation = (
                random.uniform(0.05, 0.12)
                * self.severity
            )

        elif self.planned_fault == SEAL_WEAR:
            degradation = (
                random.uniform(0.07, 0.15)
                * self.severity
            )

        elif self.planned_fault == VALVE_STICKING:
            degradation = (
                random.uniform(0.08, 0.18)
                * self.severity
            )

        else:
            degradation = 0.0

        self.health = self.clamp(
            self.health - degradation,
            0,
            MAX_HEALTH,
        )

    def update_sensors(self, step_number):
        """Generate normal readings and apply fault physics."""

        self.update_load(step_number)
        self.update_fault_state(step_number)

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
            ),
        }

        values = FaultEngineV21.apply_persistent_fault(
            values,
            self.planned_fault,
            self.severity,
        )

        values = self.update_valve_event(values)

        # Thermal inertia
        self.temperature += (
            values["temperature_target"]
            - self.temperature
        ) * random.uniform(0.08, 0.18)

        self.pressure = self.clamp(
            values["pressure"],
            3.4,
            6.2,
        )

        self.flow = self.clamp(
            values["flow"],
            7.5,
            12.5,
        )

        self.speed = self.clamp(
            values["speed"],
            80,
            132,
        )

        self.temperature = self.clamp(
            self.temperature,
            25,
            65,
        )

        self.vibration = self.clamp(
            values["vibration"],
            0.1,
            4.5,
        )

        self.update_health()

    def simulate_step(self, step_number):
        self.update_position()
        self.update_sensors(step_number)

    def get_state(self):
        return {
            "Pressure": round(self.pressure, 2),
            "Temperature": round(
                self.temperature,
                2,
            ),
            "Position": self.position,
            "Flow": round(self.flow, 2),
            "Speed": round(self.speed, 2),
            "CycleCount": self.cycle_count,
            "Health": round(self.health, 2),
            "Fault": self.fault,
            "Vibration": round(
                self.vibration,
                2,
            ),
            "Load": round(self.load, 2),
        }

    def get_metadata(self):
        """Return non-feature simulation metadata."""

        return {
            "PlannedFault": self.planned_fault,
            "Severity": round(self.severity, 4),
            "Direction": self.direction,
            "LoadPhase": self.load_phase_index + 1,
            "ValveEvent": int(
                self.valve_event_active
            ),
        }