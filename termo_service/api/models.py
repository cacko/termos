from typing import Optional
from pydantic import BaseModel, AwareDatetime
from datetime import datetime, timezone

from termo_service.ble.models import SensorLocation


class BaseResponse(BaseModel):

    def __init__(self, *args, **kwds):
        for k, v in kwds.items():
            match v:
                case datetime():
                    kwds[k] = v.replace(tzinfo=timezone.utc)
        super().__init__(*args, **kwds)

    def model_dump(self, *args, **kwds):
        return super().model_dump(mode="json")
    
    
class DataResponse(BaseResponse):
    temp: float
    humid: float
    timestamp: AwareDatetime
    location: SensorLocation
    temp_min: Optional[float] = None
