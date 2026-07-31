"""
Digital Twin - Pneumatic Cylinder
System Constants
"""

# ==========================================
# CYLINDER SPECIFICATIONS
# ==========================================

CYLINDER_NAME = "Double Acting Pneumatic Cylinder"

STROKE_LENGTH = 100          # mm

MAX_PRESSURE = 6.0           # bar
MIN_PRESSURE = 5.0           # bar

MAX_SPEED = 130              # mm/s
MIN_SPEED = 110              # mm/s

NORMAL_TEMPERATURE = 30      # Celsius
NORMAL_PRESSURE = 5.5

NORMAL_FLOW = 10             # L/min


# ==========================================
# HEALTH SCORE
# ==========================================

MAX_HEALTH = 100


# ==========================================
# FAULT TYPES
# ==========================================

HEALTHY = "Healthy"

AIR_LEAKAGE = "Air Leakage"

SEAL_WEAR = "Seal Wear"

VALVE_STICKING = "Valve Sticking"

PRESSURE_DROP = "Pressure Drop"


# ==========================================
# SIMULATION SETTINGS
# ==========================================

TIME_STEP = 1                # second

SIMULATION_SPEED = 1