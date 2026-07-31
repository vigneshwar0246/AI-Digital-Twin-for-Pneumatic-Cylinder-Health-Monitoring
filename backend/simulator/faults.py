"""
Fault Simulation Module
"""

import random

from backend.config.constants import *


class FaultEngine:

    @staticmethod
    def apply_fault(cylinder):

        # ---------------------------------
        # Healthy Condition
        # ---------------------------------

        if cylinder.cycle_count < 20:

            cylinder.fault = HEALTHY
            return

        # ---------------------------------
        # Select Random Fault
        # ---------------------------------

        fault = random.choice([
            AIR_LEAKAGE,
            SEAL_WEAR,
            VALVE_STICKING
        ])

        cylinder.fault = fault

        # ---------------------------------
        # AIR LEAKAGE
        # ---------------------------------

        if fault == AIR_LEAKAGE:

            cylinder.pressure -= random.uniform(0.5, 1.0)

            cylinder.flow += random.uniform(1.0, 2.0)

            cylinder.speed -= random.uniform(10, 20)

            cylinder.health -= random.randint(1, 3)

        # ---------------------------------
        # SEAL WEAR
        # ---------------------------------

        elif fault == SEAL_WEAR:

            cylinder.temperature += random.uniform(0.5, 1.5)

            cylinder.speed -= random.uniform(5, 10)

            cylinder.health -= random.randint(2, 4)

        # ---------------------------------
        # VALVE STICKING
        # ---------------------------------

        elif fault == VALVE_STICKING:

            cylinder.speed -= random.uniform(20, 35)

            cylinder.pressure -= random.uniform(0.2, 0.5)

            cylinder.health -= random.randint(3, 5)

        # ---------------------------------
        # Health Limit
        # ---------------------------------

        if cylinder.health < 0:
            cylinder.health = 0