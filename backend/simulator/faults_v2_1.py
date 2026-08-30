"""
Dataset V2.1 fault physics.

Provides gradual fault development, a detection threshold,
and distinct but still overlapping physical fault mechanisms.
"""

import random

from backend.config.constants import (
    HEALTHY,
    AIR_LEAKAGE,
    PRESSURE_DROP,
    SEAL_WEAR,
    VALVE_STICKING,
)


class FaultEngineV21:

    FAULT_TYPES = [
        HEALTHY,
        AIR_LEAKAGE,
        PRESSURE_DROP,
        SEAL_WEAR,
        VALVE_STICKING,
    ]

    # Below this severity, the change is considered incipient
    # and is labelled Healthy because it is not reliably detectable.
    DETECTION_THRESHOLD = 0.15

    @staticmethod
    def calculate_severity(
        step,
        fault_start,
        rise_time,
        maximum_severity,
    ):
        """Calculate smooth S-curve fault progression."""

        if fault_start is None or step < fault_start:
            return 0.0

        progress = (
            step - fault_start + 1
        ) / rise_time

        progress = max(
            0.0,
            min(1.0, progress),
        )

        # Smoothstep progression
        smooth_progress = (
            progress
            * progress
            * (3.0 - 2.0 * progress)
        )

        severity = (
            maximum_severity
            * smooth_progress
        )

        return round(
            min(maximum_severity, severity),
            4,
        )

    @classmethod
    def detectable_label(
        cls,
        planned_fault,
        severity,
    ):
        """
        Return Healthy while a fault is too weak to be
        distinguished reliably from normal sensor noise.
        """

        if planned_fault == HEALTHY:
            return HEALTHY

        if severity < cls.DETECTION_THRESHOLD:
            return HEALTHY

        return planned_fault

    @staticmethod
    def apply_persistent_fault(
        values,
        planned_fault,
        severity,
    ):
        """Apply the persistent physical effect of a fault."""

        if (
            planned_fault == HEALTHY
            or severity <= 0
        ):
            return values

        if planned_fault == AIR_LEAKAGE:

            # Persistent air loss:
            # pressure decreases while air consumption rises
            values["pressure"] -= (
                random.uniform(0.15, 0.55)
                * severity
            )

            values["flow"] += (
                random.uniform(0.25, 0.75)
                * severity
            )

            values["speed"] -= (
                random.uniform(1.0, 5.0)
                * severity
            )

            values["temperature_target"] += (
                random.uniform(0.5, 2.5)
                * severity
            )

            values["vibration"] += (
                random.uniform(0.15, 0.60)
                * severity
            )

        elif planned_fault == PRESSURE_DROP:

            # Supply-pressure problem:
            # both pressure and flow decrease persistently
            values["pressure"] -= (
                random.uniform(0.45, 1.10)
                * severity
            )

            values["flow"] -= (
                random.uniform(0.25, 0.75)
                * severity
            )

            values["speed"] -= (
                random.uniform(2.0, 8.0)
                * severity
            )

            values["temperature_target"] += (
                random.uniform(0.0, 1.5)
                * severity
            )

            values["vibration"] += (
                random.uniform(0.10, 0.50)
                * severity
            )

        elif planned_fault == SEAL_WEAR:

            # Friction-related degradation:
            # temperature and vibration rise gradually,
            # while pressure and flow remain near normal
            values["pressure"] -= (
                random.uniform(0.05, 0.20)
                * severity
            )

            values["flow"] += (
                random.uniform(0.00, 0.15)
                * severity
            )

            values["speed"] -= (
                random.uniform(1.0, 5.0)
                * severity
            )

            values["temperature_target"] += (
                random.uniform(5.0, 14.0)
                * severity
            )

            values["vibration"] += (
                random.uniform(0.50, 1.60)
                * severity
            )

        elif planned_fault == VALVE_STICKING:

            # Base valve degradation remains moderate.
            # Strong intermittent events are applied separately.
            values["pressure"] += (
                random.uniform(-0.20, 0.15)
                * severity
            )

            values["flow"] -= (
                random.uniform(0.10, 0.40)
                * severity
            )

            values["speed"] -= (
                random.uniform(1.0, 6.0)
                * severity
            )

            values["temperature_target"] += (
                random.uniform(1.0, 4.0)
                * severity
            )

            values["vibration"] += (
                random.uniform(0.30, 1.00)
                * severity
            )

        return values

    @staticmethod
    def apply_valve_event(
        values,
        severity,
    ):
        """
        Apply a temporary sticking/stall event.

        The cylinder module will maintain the event for
        multiple steps, producing temporal irregularity.
        """

        values["pressure"] += (
            random.uniform(-0.60, 0.35)
            * severity
        )

        values["flow"] -= (
            random.uniform(0.80, 1.50)
            * severity
        )

        values["speed"] -= (
            random.uniform(15.0, 30.0)
            * severity
        )

        values["vibration"] += (
            random.uniform(1.00, 2.20)
            * severity
        )

        return values