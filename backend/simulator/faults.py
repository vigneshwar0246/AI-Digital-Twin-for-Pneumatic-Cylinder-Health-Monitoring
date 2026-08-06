"""
Fault Simulation Module
Digital Twin Fault Progression Model
"""

import random

from backend.config.constants import *


class FaultEngine:

    @staticmethod
    def apply_fault(cylinder):

        # =====================================
        # Healthy Region
        # =====================================

        if cylinder.cycle_count < 20:
            cylinder.fault = HEALTHY
            return

        # =====================================
        # Select Fault (only once)
        # =====================================

        if cylinder.fault == HEALTHY:

            fault_probability = random.random()

            if fault_probability < 0.45:
                cylinder.fault = AIR_LEAKAGE

            elif fault_probability < 0.70:
                cylinder.fault = SEAL_WEAR

            elif fault_probability < 0.90:
                cylinder.fault = VALVE_STICKING

            else:
                cylinder.fault = PRESSURE_DROP

        # =====================================
        # AIR LEAKAGE
        # =====================================

        if cylinder.fault == AIR_LEAKAGE:

            cylinder.pressure -= random.uniform(0.3, 0.6)
            cylinder.flow += random.uniform(0.5, 1.2)
            cylinder.speed -= random.uniform(5, 10)
            cylinder.health -= random.uniform(0.05, 0.15)

        # =====================================
        # SEAL WEAR
        # =====================================

        elif cylinder.fault == SEAL_WEAR:

            cylinder.temperature += random.uniform(0.2, 0.5)
            cylinder.speed -= random.uniform(8, 15)
            cylinder.health -= random.uniform(0.10, 0.25)

        # =====================================
        # VALVE STICKING
        # =====================================

        elif cylinder.fault == VALVE_STICKING:

            cylinder.speed -= random.uniform(15, 25)
            cylinder.pressure -= random.uniform(0.2, 0.5)
            cylinder.health -= random.uniform(0.20, 0.40)

        # =====================================
        # PRESSURE DROP
        # =====================================

        elif cylinder.fault == PRESSURE_DROP:

            cylinder.pressure -= random.uniform(0.5, 0.9)
            cylinder.speed -= random.uniform(3, 8)
            cylinder.flow -= random.uniform(0.5, 1.0)
            cylinder.health -= random.uniform(0.08, 0.20)

        # =====================================
        # Keep values within limits
        # =====================================

        cylinder.pressure = max(
            MIN_PRESSURE,
            min(MAX_PRESSURE, cylinder.pressure)
        )

        cylinder.speed = max(
            MIN_SPEED,
            min(MAX_SPEED, cylinder.speed)
        )

        cylinder.flow = max(8.0, min(12.0, cylinder.flow))

        cylinder.health = max(
            0,
            round(cylinder.health, 2)
        )