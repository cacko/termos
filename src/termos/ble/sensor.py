import asyncio
import logging
from queue import Queue
from typing import Any
from termos.ble.models import SensorLocation
import subprocess

class SensorMeta(type):

    instances: dict[str, "Sensor"] = {}
    queues: dict[str, Queue] = {}
    notifiers: dict[str, asyncio.Future] = {}

    def __call__(cls, *args: Any, **kwds: Any) -> 'Sensor':
        k = cls.__name__
        if k not in cls.instances:
            cls.instances[k] = type.__call__(cls, *args, **kwds)
        return cls.instances[k]

    def register(cls, ui_queue: Queue):
        cls.queues[cls.__name__] = ui_queue

    @property
    def queue(cls) -> Queue:
        return cls.queues[cls.__name__]

    async def start_notify(cls):
        await cls().init_notify()

    def restart_notify(cls):
        cls.start_notify()

    def stop(cls):
        try:
            cls().stop_notify()
        except Exception:
            pass

    def stop_notify(cls):
        try:
            cls().disconnect()
            logging.info(f"STOP NOTIFY {cls.__name__}")
        except AssertionError:
            pass


class Sensor(object, metaclass=SensorMeta):

    mac: str
    address: str
    uuid_read: str
    uuid_write: str
    location: SensorLocation

        
    async def init_notify(self):
        raise NotImplementedError
    
    @property
    def is_connected(self) -> bool:
        output = subprocess.run(
            ["bluetoothctl", "devices"],
            capture_output=True,
            text=True,
        )
        return self.mac in output.stdout
    
    def disconnect(self):
        subprocess.run(
            ["bluetoothctl", "disconnect", self.mac],
            capture_output=False,
            text=True,
        )
