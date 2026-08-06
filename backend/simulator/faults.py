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
        # HEALTHY (0 - 500 Cycles)
        # =====================================

        if cylinder.cycle_count <= 500:

            cylinder.fault = HEALTHY

            cylinder.health = max(
                95,
                cylinder.health - random.uniform(0.00, 0.02)
            )

        # =====================================
        # AIR LEAKAGE (501 - 1700 Cycles)
        # =====================================

        elif cylinder.cycle_count <= 1700:

            cylinder.fault = AIR_LEAKAGE

            cylinder.pressure -= random.uniform(0.2, 0.5)

            cylinder.flow += random.uniform(0.4, 1.0)

            cylinder.speed -= random.uniform(3, 8)

            cylinder.health = max(
                75,
                cylinder.health - random.uniform(0.02, 0.05)
            )

        # =====================================
        # PRESSURE DROP (1701 - 3000 Cycles)
        # =====================================

        elif cylinder.cycle_count <= 3000:

            cylinder.fault = PRESSURE_DROP

            cylinder.pressure -= random.uniform(0.5, 0.9)

            cylinder.flow -= random.uniform(0.3, 0.8)

            cylinder.speed -= random.uniform(6, 12)

            cylinder.health = max(
                55,
                cylinder.health - random.uniform(0.04, 0.08)
            )

        # =====================================
        # SEAL WEAR (3001 - 4200 Cycles)
        # =====================================

        elif cylinder.cycle_count <= 4200:

            cylinder.fault = SEAL_WEAR

            cylinder.temperature += random.uniform(0.2, 0.6)

            cylinder.speed -= random.uniform(8, 15)

            cylinder.health = max(
                30,
                cylinder.health - random.uniform(0.05, 0.10)
            )

        # =====================================
        # VALVE STICKING (4201+ Cycles)
        # =====================================

        else:

            cylinder.fault = VALVE_STICKING

            cylinder.speed -= random.uniform(12, 20)

            cylinder.pressure -= random.uniform(0.3, 0.7)

            cylinder.flow -= random.uniform(0.2, 0.6)

            cylinder.health = max(
                0,
                cylinder.health - random.uniform(0.08, 0.15)
            )

        # =====================================
        # Sensor Limits
        # =====================================

        cylinder.pressure = max(
            MIN_PRESSURE,
            min(MAX_PRESSURE, cylinder.pressure)
        )

        cylinder.speed = max(
            MIN_SPEED,
            min(MAX_SPEED, cylinder.speed)
        )

        cylinder.health = round(cylinder.health, 2)