from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class SensorReading(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pressure: float = Field(ge=0, le=12)
    temperature: float = Field(ge=-20, le=120)
    position: float = Field(ge=0, le=100)
    flow: float = Field(ge=0, le=30)
    speed: float = Field(ge=0, le=250)
    vibration: float = Field(ge=0, le=15)
    load: float = Field(ge=0, le=100)
    cycle_count: int | None = Field(default=None, ge=0)

    def feature_dict(self):
        return {k.title(): getattr(self, k) for k in ("pressure","temperature","position","flow","speed","vibration","load")}


class PredictionRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    reading: SensorReading


class BatchPredictionRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    readings: list[SensorReading] = Field(min_length=1, max_length=1000)
    reset_buffer: bool = False


class SimulationCreateRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    planned_fault: str = "Healthy"
    seed: int | None = None
    fault_start: int | None = Field(default=40, ge=0)
    maximum_severity: float = Field(default=.8, ge=0, le=1)
    rise_time: int = Field(default=80, ge=1)


class ErrorBody(BaseModel):
    error: dict
