"""
Virtual Sensors for the Digital Twin
"""

import random


class VirtualSensors:

    @staticmethod
    def get_pressure():

        # Normal operating pressure
        return round(random.uniform(5.2, 5.8), 2)

    @staticmethod
    def get_temperature(current_temp):

        # Temperature slowly increases
        current_temp += random.uniform(0.0, 0.2)

        return round(current_temp, 2)

    @staticmethod
    def get_flow():

        return round(random.uniform(9.5, 10.5), 2)

    @staticmethod
    def get_speed():

        return round(random.uniform(115, 125), 2)