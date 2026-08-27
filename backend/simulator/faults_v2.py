"""
Dataset V2 Fault Simulation

Creates gradual and overlapping pneumatic-cylinder fault patterns
without directly assigning faults from CycleCount.
"""

import random

from backend.config.constants import (
    HEALTHY,
    AIR_LEAKAGE,
    PRESSURE_DROP,
    SEAL_WEAR,
    VALVE_STICKING
)


class FaultEngineV2:

    FAULT_TYPES = [
        HEALTHY,
        AIR_LEAKAGE,
        PRESSURE_DROP,
        SEAL_WEAR,
        VALVE_STICKING
    ]

    @staticmethod
    def calculate_severity(step, fault_start, rise_time, maximum_severity):
        """
        Gradually increases fault severity after fault_start.
        """

        if fault_start is None or step < fault_start:
            return 0.0

        progress = (step - fault_start + 1) / rise_time

        severity = min(maximum_severity, progress * maximum_severity)

        return round(severity, 4)

    @staticmethod
    def apply_fault(values, fault, severity):
        """
        Modifies sensor values according to fault and severity.

        Overlapping random ranges prevent fault classes from
        becoming perfectly separated.
        """

        if fault == HEALTHY or severity <= 0:
            return values

        if fault == AIR_LEAKAGE:

            values["pressure"] -= random.uniform(0.10, 0.65) * severity
            values["flow"] += random.uniform(0.15, 0.85) * severity
            values["speed"] -= random.uniform(1.5, 7.5) * severity
            values["temperature_target"] += random.uniform(0.5, 4.0) * severity
            values["vibration"] += random.uniform(0.20, 1.00) * severity

        elif fault == PRESSURE_DROP:

            values["pressure"] -= random.uniform(0.25, 1.00) * severity
            values["flow"] -= random.uniform(0.10, 0.70) * severity
            values["speed"] -= random.uniform(3.0, 11.0) * severity
            values["temperature_target"] += random.uniform(0.0, 3.0) * severity
            values["vibration"] += random.uniform(0.25, 1.10) * severity

        elif fault == SEAL_WEAR:

            values["pressure"] -= random.uniform(0.00, 0.25) * severity
            values["flow"] += random.uniform(0.00, 0.35) * severity
            values["speed"] -= random.uniform(2.0, 9.0) * severity
            values["temperature_target"] += random.uniform(3.0, 12.0) * severity
            values["vibration"] += random.uniform(0.50, 2.20) * severity

        elif fault == VALVE_STICKING:

            values["pressure"] += random.uniform(-0.55, 0.25) * severity
            values["flow"] += random.uniform(-0.65, 0.35) * severity
            values["speed"] -= random.uniform(4.0, 15.0) * severity
            values["temperature_target"] += random.uniform(2.0, 9.0) * severity
            values["vibration"] += random.uniform(0.80, 3.00) * severity

            # Occasional irregular valve movement
            if random.random() < 0.08 * severity:
                values["speed"] -= random.uniform(3.0, 8.0)

        return values