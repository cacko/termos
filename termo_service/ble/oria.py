import asyncio
import logging
from asyncio import Queue, QueueEmpty
from bleak import BleakClient
from bleak.backends.device import BLEDevice
from bleak import BleakScanner
from termo_service.config import app_config
from termo_service.ble.sensor import Sensor
from termo_service.ble.models import NowData, Status, StatusChange
from termo_service.ble.oria_protocol import (
    TBCmdQuery,
    TBCmdReset,
    TBMsgQuery,
    TBCmdDump,
    TB,
    TBMsgDump,
)


def convert_to_readings(response):
    readings = []
    for v in range(6):
        results_position = 6 + (v * 2)
        reading = int.from_bytes(
            response[results_position : results_position + 2], byteorder="little"
        )
        reading = reading * 0.0625
        if reading > 2048:
            reading = -1 * (4096 - reading)
        readings.append("{:.2f}".format(reading))
    print(",".join(readings))


def notification_oria(sender: int, data: bytearray):
    header = TB(int(data.hex()[:2]))
    match header:
        case TB.QUERY:
            try:
                query = TBMsgQuery(data)
                assert query.count > 0
                Oria.ble_queue.put_nowait(
                    (TBCmdDump(start=query.count-1, count=1).get_msg(), 0)
                )
            except AssertionError:
                Oria.ble_queue.put_nowait((TBCmdQuery().get_msg(), 10))

        case TB.DUMP:
            msg = TBMsgDump(data)
            logging.debug([msg.count, msg.offset, msg.data])
            Oria.ble_queue.put_nowait((TBCmdReset().get_msg(), 10))
            Oria.ble_queue.put_nowait((TBCmdQuery().get_msg(), 120))
            nowdata = NowData(
                temp=msg.data[0].get("t"),
                humid=msg.data[0].get("h"),
                location=Oria.location,
            )
            Oria.queue.put_nowait(nowdata)


def disconnect_oria(client: BleakClient):
    logging.info(f"{client.address} disconnected")
    Oria.queue.put_nowait(
        StatusChange(status=Status.DISCONNECTED, location=Oria.location)
    )


class Oria(Sensor):

    ble_queue: Queue = Queue()
    datapoints_count = 0

    @property
    async def device(self) -> BLEDevice:
        device: BLEDevice = None
        while not device:
            devices = await BleakScanner.discover()
            device = next(
                filter(lambda x: x.address == app_config.ble.oria.address, devices),
                None,
            )
        logging.info(f"found device {device.details}")
        return device

    async def init_notify(self):
        device = await self.device
        async with BleakClient(device, disconnected_callback=disconnect_oria) as client:
            Oria.queue.put_nowait(
                StatusChange(status=Status.CONNECTED, location=self.location)
            )
            logging.info(f"connected to {client.address}")
            Oria.ble_queue.put_nowait((TBCmdQuery().get_msg(), 0))
            await client.start_notify(
                app_config.ble.oria.uuid_read, callback=notification_oria
            )
            while client.is_connected:
                try:
                    cmd, slp = Oria.ble_queue.get_nowait()
                    await asyncio.sleep(slp)
                    await client.write_gatt_char(app_config.ble.oria.uuid_write, cmd)
                    Oria.ble_queue.task_done()
                except QueueEmpty:
                    await asyncio.sleep(0.2)
                except Exception as e:
                    logging.exception(e)
                    await client.stop_notify(app_config.ble.oria.uuid_read)
            await client.disconnect()
