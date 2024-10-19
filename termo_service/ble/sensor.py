import asyncio
from asyncio import BaseEventLoop
import logging
from queue import Queue
from typing import Any
from corethread import StoppableThread
from termo_service.ble.models import SensorLocation
from termo_service.config import BleDeviceConfig


class SensorMeta(type):

    instances: dict[str, "Sensor"] = {}
    queues: dict[str, Queue] = {}
    notifiers: dict[str, asyncio.Future] = {}
    threads: dict[str, StoppableThread] = {}

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

    def start_notify(cls):
        loop: BaseEventLoop = asyncio.new_event_loop()

        def bleak_thread(loop: BaseEventLoop):
            asyncio.set_event_loop(loop)
            loop.run_forever()

        cls.threads[cls.__name__] = StoppableThread(target=bleak_thread, args=(loop,))
        cls.threads[cls.__name__].start()
        cls.notifiers[cls.__name__] = asyncio.run_coroutine_threadsafe(
            cls().init_notify(), loop
        )
        return cls.threads[cls.__name__]

    def restart_notify(cls):
        cls.threads[cls.__name__].stop()
        cls.start_notify()

    def stop(cls):
        try:
            cls.stop_notify()
        except Exception:
            pass

    def stop_notify(cls):
        try:
            assert cls.notifiers[cls.__name__]
            assert cls.notifiers[cls.__name__].cancel()
            logging.info(f"STOP NOTIFY")
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
