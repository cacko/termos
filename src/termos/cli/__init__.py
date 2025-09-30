from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError
from typing_extensions import Annotated
import rich
import typer
from termos.ble.models import SensorLocation
from termos.db import create_tables
from termos.db.models.data import Data, PeriodChunk
import asyncio

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
                
@cli.command()
def discover():
    async def a_discover():
        devices = await BleakScanner.discover(return_adv=True)
        for device, adv in devices.values():
            rich.print([device, adv])
            try:
                async with BleakClient(device) as client:
                    for service in client.services:
                        for char in service.characteristics:
                            rich.print(char.properties)
                            rich.print(char.uuid)
            except BleakError as e:
                rich.print(f"BleakError occurred while connecting to {device}: {e}")
            except asyncio.TimeoutError as e:
                rich.print(f"Timeout occurred while connecting to {device}: {e}")
    asyncio.run(a_discover())
    


@cli.callback()
def main(ctx: typer.Context):
    pass
