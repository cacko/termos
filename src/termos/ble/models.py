from enum import StrEnum
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class SensorType(StrEnum):
    TP357 = "tp357"
    ORIA = "oria"
    HTTP = "http"

class Status(StrEnum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    LOADED = "loaded"


class Command(StrEnum):
    STATUS = "status"
    DATA = "data"
    

class SensorLocation(StrEnum):
    INDOOR = "indoor"
    OUTDOOR = "outdoor"


class StatusChange(BaseModel):
    model: str = Field(default="status_change")
    status: Status
    location: SensorLocation

class NowData(BaseModel):
    temp: float
    humid: float
    location: SensorLocation
    timestamp: Optional[datetime] = None
    model: str = Field(default="now_data")

    def __init__(self, **kwds):
        kwds.setdefault("timestamp", datetime.now(tz=timezone.utc))
        super().__init__(**kwds)
    
    def __eq__(self, value: "NowData") -> bool:
        return all([self.temp == value.temp, self.humid == value.humid])