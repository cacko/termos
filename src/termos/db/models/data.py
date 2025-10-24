from enum import StrEnum
import logging
from termos.api.models import DataResponse
from termos.sensor.models import SensorLocation
from termos.db.fields import LocationField
from .base import DbModel
from termos.db.database import Database
from peewee import FloatField, DateTimeField, fn
from playhouse.shortcuts import model_to_dict
from datetime import timezone, datetime, timedelta
from playhouse.postgres_ext import DateTimeTZField


class PeriodChunk(StrEnum):
    DAY = "day"
    HOUR = "hour"
    WEEK = "week"


class Data(DbModel):
    temp = FloatField()
    humid = FloatField()
    timestamp = DateTimeTZField(default=datetime.utcnow)
    location = LocationField(null=False)

    @classmethod
    def get_last_data(cls, location: SensorLocation) -> DataResponse:
        record: Data = (
            Data.select()
            .where(Data.location == location)
            .order_by(Data.timestamp.desc())
            .limit(1)
            .get()
        )
        return record.to_response()

    @classmethod
    def get_period(
        cls, chunk: PeriodChunk, location: SensorLocation
    ) -> list[DataResponse]:
        
        match chunk:
            case PeriodChunk.DAY:
                interval = timedelta(days=1)
                truncate = "1 hour"
                timestamp = fn.date_bin(truncate, Data.timestamp, fn.now())
            case PeriodChunk.WEEK:
                interval = timedelta(days=14)
                truncate = "1 day"
                timestamp = fn.date_bin(truncate, Data.timestamp, datetime.now().date())
            case PeriodChunk.HOUR:
                interval = timedelta(hours=1)
                truncate = "5 minute"
                timestamp = fn.date_bin(truncate, Data.timestamp, fn.now())
        filters = [
            Data.timestamp >= (datetime.now(timezone.utc) - interval),
            Data.location == location
        ]

        query = (
            
            Data.select(
                fn.MAX(Data.temp).alias("temp"),
                fn.MAX(Data.humid).alias("humid"),
                fn.MIN(Data.temp).alias("temp_min"),
                timestamp.alias("timestamp"),
                Data.location
            )
            .where(*filters)
            .group_by(timestamp, Data.location)
            .order_by(timestamp.asc())
            .dicts()
        )
        return [DataResponse(**r) for r in query]

    def to_response(self, **kwds):
        return DataResponse(
            temp=self.temp,
            humid=self.humid,
            timestamp=self.timestamp,
            location=self.location,
        )

    def to_dict(self):
        data = model_to_dict(self)
        ts: datetime.datetime = data["timestamp"]
        data["timestamp"] = ts
        return data

    class Meta:
        database = Database.db
        table_name = "tempo_data"
        order_by = ["-timestamp"]
        indexes = ((("timestamp","location"), True),)
