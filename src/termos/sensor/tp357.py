import asyncio
import logging
from bleak import BleakClient
from bleak.backends.device import BLEDevice
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak import BleakScanner
from termos.sensor.sensor import Sensor
from termos.sensor.models import NowData, SensorLocation, Status, StatusChange


def tp357_result(data: bytearray, location: SensorLocation):
    temp = (data[3] + data[4] * 256) / 10
    humid = data[5]
    return NowData(temp=temp, humid=humid, location=location)


class TP357(Sensor):

    @property
    async def device(self) -> BLEDevice:
        device: BLEDevice = None
        while not device:
            devices = await BleakScanner.discover()
            device = next(
                filter(lambda x: x.address == self.address, devices),
                None,
            )
        logging.info(f"found device {device.details}")
        return device

    def notification_tp357(self, sender: BleakGATTCharacteristic, data: bytearray):
        res = tp357_result(data, self.location)
        logging.debug(res)
        self.__class__.queue.put_nowait((res, self.__class__))

    def disconnect_tp357(self, client: BleakClient):
        logging.info(f"{client.address} disconnected")
        self.__class__.queue.put_nowait(
            (
                StatusChange(
                    status=Status.DISCONNECTED,
                    location=self.location,
                ),
                self.__class__,
            )
        )

    async def init_notify(self):
        device = await self.device
        async with BleakClient(
            device, disconnected_callback=self.disconnect_tp357
        ) as client:
            self.__class__.queue.put_nowait(
                (
                    StatusChange(
                        status=Status.CONNECTED,
                        location=self.location,
                    ),
                    self.__class__,
                )
            )
            logging.info(f"connected to {client.address}")
            read = client.services.get_characteristic(self.uuid_read)
            await client.start_notify(read, callback=self.notification_tp357)
            while client.is_connected:
                try:
                    await asyncio.sleep(0.5)
                except Exception as e:
                    logging.exception(e)
                    await client.stop_notify(read)
            await client.disconnect()
