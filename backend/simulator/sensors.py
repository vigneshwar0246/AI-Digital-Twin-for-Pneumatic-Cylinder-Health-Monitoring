"""
Virtual Sensors for the Digital Twin
"""

import random

from backend.config.constants import *


class VirtualSensors:

    @staticmethod
    def get_pressure(load=15):

        """
        Higher load requires higher pressure.
        """

        pressure = NORMAL_PRESSURE + (load / MAX_LOAD) * 0.5

        pressure += random.uniform(-0.10, 0.10)

        return round(pressure, 2)

    @staticmethod
    def get_temperature(current_temp):

        """
        Temperature slowly increases.
        """

        current_temp += random.uniform(0.0, 0.2)

        return round(current_temp, 2)

    @staticmethod
    def get_flow():

        """
        Air flow fluctuates slightly.
        """

        return round(random.uniform(9.5, 10.5), 2)

    @staticmethod
    def get_speed(load=15):

        """
        Higher load decreases cylinder speed.
        """

        speed = MAX_SPEED - (load / MAX_LOAD) * 12

        speed += random.uniform(-2, 2)

        return round(speed, 2)