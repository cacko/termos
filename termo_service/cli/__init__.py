import logging
from bleak import BleakClient
from typing_extensions import Annotated
import rich
import typer
import termo_service
from termo_service.ble.models import SensorLocation
import termo_service.config
from termo_service.db import create_tables
from termo_service.db.models.data import Data, PeriodChunk
from asyncer import asyncify, syncify
import anyio

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
def oria():
    
    from termo_service.config import app_config
    import asyncio
    from termo_service.ble.oria_protocol import (
        TBCmdBase,
        TBCmdQuery,
        TBMsgQuery,
        TBCmdDump,
        TB_COMMAND_DUMP,
        TBMsgDump,
    )

    client = BleakClient(app_config.ble.oria.address)
    TX_CHAR_UUID = app_config.ble.oria.uuid_write
    RX_CHAR_UUID = app_config.ble.oria.uuid_read
    cmd = TBCmdQuery()
    syncify(client.write_gatt_char)(TX_CHAR_UUID, cmd.get_msg())
    data = syncify(client.read_gatt_char)(RX_CHAR_UUID)
    resp = TBMsgQuery()
    print("01:" + data.hex())

    logging.info(f"connected to {client.address}")

    def notification_oria(sender: int, data: bytearray):
        if data is None:
            return
        try:
            hdata = data.hex()
            msg = TBMsgDump(data)
            print(msg.offset, msg.count, msg.data)
            # print(f"{sender}: {hdata}")
        except Exception as exc:
            print(str(exc))

    syncify(client.start_notify)(RX_CHAR_UUID, callback=notification_oria)
    cmd_dump = bytes(
        [
            TB_COMMAND_DUMP,
            0,
            0,
            resp.count & 0xFF,
            (resp.count >> 8) & 0xFF,
            (resp.count >> 16) & 0xFF,
            1,
        ]
    )
    cnt = 0
    while cnt < resp.count:
        c = 15 if resp.count - cnt > 15 else resp.count - cnt
        cmd = TBCmdDump(cnt, c)
        cmd_dump = cmd.get_msg()
        cnt += c
        # print('cmd ', cmd_dump.hex())
        syncify(client.write_gatt_char)(TX_CHAR_UUID, cmd_dump)
    syncify(asyncio.sleep)(0.5)
    data = syncify(client.read_gatt_char)(RX_CHAR_UUID)
    print(data.hex())
    syncify(client.disconnect)()


@cli.callback()
def main(ctx: typer.Context):
    pass
