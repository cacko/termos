from fastapi import APIRouter, Depends, Path, HTTPException
from typing import Annotated
from termo_service.api.models import DataResponse
from termo_service.ble.models import SensorLocation
from termo_service.db.models.data import Data, PeriodChunk
from termo_service.api.auth import check_auth

router = APIRouter()


@router.get("/now/{location}")
def api_now(
    location: Annotated[SensorLocation, Path(title="sensor location")],
    auth_user=Depends(check_auth),
):
    try:
        response: DataResponse = Data.get_last_data(location=location)
        return response.model_dump()
    except AssertionError:
        raise HTTPException(404)


@router.get("/hour/{location}")
def api_period_hour(
    location: Annotated[SensorLocation, Path(title="sensor location")],
    auth_user=Depends(check_auth),
):
    try:
        records = Data.get_period(chunk=PeriodChunk.HOUR, location=location)
        return [r.model_dump() for r in records]
    except AssertionError:
        raise HTTPException(404)


@router.get("/day/{location}")
def api_period_day(
    location: Annotated[SensorLocation, Path(title="sensor location")],
    auth_user=Depends(check_auth),
):
    try:
        records = Data.get_period(chunk=PeriodChunk.DAY, location=location)
        return [r.model_dump() for r in records]
    except AssertionError:
        raise HTTPException(404)


@router.get("/week/{location}")
def api_period_week(
    location: Annotated[SensorLocation, Path(title="sensor location")],
    auth_user=Depends(check_auth),
):
    try:
        records = Data.get_period(chunk=PeriodChunk.WEEK, location=location)
        return [r.model_dump() for r in records]
    except AssertionError:
        raise HTTPException(404)
