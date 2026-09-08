"""
Temporal feature engineering for Dataset V2.1.

All rolling features use only readings from the same
simulation run, preventing information leakage.
"""

import pandas as pd
from collections import defaultdict, deque

from backend.config.constants import MAX_LOAD


ROLLING_WINDOW = 10

BASE_FEATURES = [
    "Pressure",
    "Temperature",
    "Position",
    "Flow",
    "Speed",
    "Vibration",
    "Load",
]

ENGINEERED_FEATURES = [
    "PressureResidual",
    "SpeedResidual",
    "TemperatureResidual",
    "VibrationResidual",
    "FlowDeviation",
    "PressureChange",
    "FlowChange",
    "SpeedChange",
    "VibrationChange",
    "PressureStd10",
    "FlowStd10",
    "SpeedStd10",
    "VibrationStd10",
    "TemperatureTrend10",
    "PositionDwell",
    "DwellRate10",
]

FEATURE_COLUMNS = (
    BASE_FEATURES
    + ENGINEERED_FEATURES
)


class OnlineFeatureBuffer:
    """Bounded, independent session buffers using the offline feature path."""

    def __init__(self, max_history=100):
        if max_history < ROLLING_WINDOW + 1:
            raise ValueError("max_history must be at least 11")
        self.max_history = max_history
        self._buffers = defaultdict(lambda: deque(maxlen=max_history))

    def add(self, session_id, reading):
        rows = self._buffers[session_id]
        row = {name: float(reading[name]) for name in BASE_FEATURES}
        rows.append(row)
        frame = pd.DataFrame(list(rows))
        frame["RunID"] = session_id
        frame["Step"] = range(len(frame))
        engineered = add_temporal_features(frame)
        features = engineered.iloc[-1][FEATURE_COLUMNS].astype(float).to_dict()
        return features, len(rows) < ROLLING_WINDOW

    def reset(self, session_id):
        self._buffers.pop(session_id, None)

    def size(self, session_id):
        return len(self._buffers.get(session_id, ()))


def rolling_standard_deviation(
    df,
    column,
):
    """Calculate within-run rolling variation."""

    return (
        df.groupby(
            "RunID",
            sort=False,
        )[column]
        .transform(
            lambda values:
            values.rolling(
                window=ROLLING_WINDOW,
                min_periods=2,
            ).std(ddof=0)
        )
        .fillna(0.0)
    )


def absolute_change(
    df,
    column,
):
    """Calculate absolute step-to-step sensor change."""

    return (
        df.groupby(
            "RunID",
            sort=False,
        )[column]
        .diff()
        .abs()
        .fillna(0.0)
    )


def add_temporal_features(df):
    """
    Add load-adjusted and temporal features.

    The target, planned fault, severity, health, time and
    cycle count are never used as model features.
    """

    required_columns = (
        BASE_FEATURES
        + ["RunID", "Step"]
    )

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    result = (
        df.sort_values(
            ["RunID", "Step"],
            kind="stable",
        )
        .reset_index(drop=True)
        .copy()
    )

    # Expected healthy readings under the current load
    expected_pressure = (
        4.9
        + (result["Load"] / MAX_LOAD) * 1.0
    )

    expected_speed = (
        129
        - (result["Load"] / MAX_LOAD) * 14
    )

    expected_temperature = (
        30
        + (result["Load"] / MAX_LOAD) * 5
    )

    expected_vibration = (
        0.30
        + (result["Load"] / MAX_LOAD) * 0.25
    )

    # Residuals isolate abnormal behaviour from load effects
    result["PressureResidual"] = (
        result["Pressure"]
        - expected_pressure
    )

    result["SpeedResidual"] = (
        result["Speed"]
        - expected_speed
    )

    result["TemperatureResidual"] = (
        result["Temperature"]
        - expected_temperature
    )

    result["VibrationResidual"] = (
        result["Vibration"]
        - expected_vibration
    )

    result["FlowDeviation"] = (
        result["Flow"] - 10.0
    )

    # Instantaneous changes
    result["PressureChange"] = absolute_change(
        result,
        "Pressure",
    )

    result["FlowChange"] = absolute_change(
        result,
        "Flow",
    )

    result["SpeedChange"] = absolute_change(
        result,
        "Speed",
    )

    result["VibrationChange"] = absolute_change(
        result,
        "Vibration",
    )

    # Rolling variation identifies intermittent sticking
    result["PressureStd10"] = (
        rolling_standard_deviation(
            result,
            "Pressure",
        )
    )

    result["FlowStd10"] = (
        rolling_standard_deviation(
            result,
            "Flow",
        )
    )

    result["SpeedStd10"] = (
        rolling_standard_deviation(
            result,
            "Speed",
        )
    )

    result["VibrationStd10"] = (
        rolling_standard_deviation(
            result,
            "Vibration",
        )
    )

    # Gradual thermal rise is important for Seal Wear
    result["TemperatureTrend10"] = (
        result.groupby(
            "RunID",
            sort=False,
        )["Temperature"]
        .diff(periods=ROLLING_WINDOW)
        .fillna(0.0)
    )

    position_change = (
        result.groupby(
            "RunID",
            sort=False,
        )["Position"]
        .diff()
    )

    result["PositionDwell"] = (
        position_change.eq(0)
        .astype(float)
    )

    result["DwellRate10"] = (
        result.groupby(
            "RunID",
            sort=False,
        )["PositionDwell"]
        .transform(
            lambda values:
            values.rolling(
                window=ROLLING_WINDOW,
                min_periods=1,
            ).mean()
        )
    )

    if result[FEATURE_COLUMNS].isna().any().any():
        raise ValueError(
            "Engineered features contain missing values."
        )

    return result
