from typing_extensions import Annotated
import rich
import typer
from termo_service.ble.models import SensorLocation
from termo_service.db import create_tables
from termo_service.db.models.data import Data, PeriodChunk

cli = typer.Typer()


@cli.command()
def init_db():
    create_tables()


@cli.command()
def now_indoor():
    record = Data.get_last_data(location=SensorLocation.INDOOR)
    rich.print(record)


@cli.command()
def period_indoor(period: Annotated[PeriodChunk, typer.Argument()]):
    records = Data.get_period(chunk=period, location=SensorLocation.INDOOR)
    rich.print([r.model_dump() for r in records])


@cli.callback()
def main(ctx: typer.Context):
    pass
