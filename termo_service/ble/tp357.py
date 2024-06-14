import asyncio
import logging
from bleak import BleakClient
from bleak.backends.device import BLEDevice
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak import BleakScanner
from termo_service.config import app_config
from termo_service.ble.sensor import Sensor
from termo_service.ble.models import NowData, Status, StatusChange


def tp357_result(data: bytearray):
    temp = (data[3] + data[4] * 256) / 10
    humid = data[5]
    return NowData(temp=temp, humid=humid, location=TP357.location)


def notification_tp357(sender: BleakGATTCharacteristic, data: bytearray):
    res = tp357_result(data)
    logging.debug(res)
    TP357.queue.put_nowait(res)


def disconnect_tp357(client: BleakClient):
    logging.info(f"{client.address} disconnected")
    TP357.queue.put_nowait(
        StatusChange(status=Status.DISCONNECTED, location=TP357.location)
    )


class TP357(Sensor):

    @property
    async def device(self) -> BLEDevice:
        device: BLEDevice = None
        while not device:
            devices = await BleakScanner.discover()
            device = next(
                filter(lambda x: x.address == app_config.ble.tp357.address, devices),
                None,
            )
        logging.info(f"found device {device.details}")
        return device

    async def init_notify(self):
        device = await self.device
        async with BleakClient(
            device, disconnected_callback=disconnect_tp357
        ) as client:
            TP357.queue.put_nowait(
                StatusChange(status=Status.CONNECTED, location=TP357.location)
            )
            logging.info(f"connected to {client.address}")
            read = client.services.get_characteristic(app_config.ble.tp357.uuid_read)
            await client.start_notify(read, callback=notification_tp357)
            while client.is_connected:
                try:
                    await asyncio.sleep(0.5)
                except Exception as e:
                    logging.exception(e)
                    await client.stop_notify(read)
            await client.disconnect()
            logging.info(f"STOPPING TP")
