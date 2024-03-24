from pydantic import BaseModel, field_validator, Field
from datetime import datetime


# FastAPI models
class AccelerometerData(BaseModel):
    x: float
    y: float
    z: float


class GpsData(BaseModel):
    latitude: float
    longitude: float
    timestamp: datetime = Field(..., title="Timestamp", description="Timestamp of the data")


class AgentData(BaseModel):
    accelerometer: AccelerometerData
    gps: GpsData
    timestamp: datetime = Field(..., title="Timestamp", description="Timestamp of the data")

    @classmethod
    @field_validator('timestamp', mode='before')
    def check_timestamp(cls, value):
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            raise ValueError( "Invalid timestamp format. Expected ISO 8601 format(YYYY-MM-DDTHH:MM:SSZ).")
        