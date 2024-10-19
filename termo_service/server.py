import asyncio
import logging
from queue import Empty, Queue
from time import sleep
from corethread import StoppableThread

from termo_service.ble.models import NowData, SensorLocation, SensorType, Status, StatusChange
from termo_service.ble.sensor import SensorMeta
from termo_service.ble.tp357 import TP357
from termo_service.ble.oria import Oria
from termo_service.db.models.data import Data
from termo_service.firebase.db import NowdataDb
from termo_service.lametric import Lametric
from termo_service.ws.router import manager


class Server(StoppableThread):

    current_data: dict[str, NowData] = {}

    def __init__(self, *args, **kwargs):
        self.queue: Queue = Queue()
        self.current_data[SensorLocation.INDOOR] = NowData(
            **Data.get_last_data(location=SensorLocation.INDOOR).model_dump()
        )
        super().__init__(*args, **kwargs)

    def run(self):

        asyncio.run(Lametric.update(self.current_data[SensorLocation.INDOOR]))
        while not self.stopped():
            try:
                payload, sender = self.queue.get_nowait()
                match payload:
                    case StatusChange():
                        self.on_status(payload, sender)
                    case NowData():
                        self.store_data(payload)
                self.queue.task_done()
            except Empty:
                logging.debug("queue empty")
                sleep(0.2)
        logging.info("STOPPING SERVER")

    def on_status(self, status: StatusChange, sender: SensorMeta):
        asyncio.run(manager.broadcast(status.model_dump(mode="json")))
        match status.status:
            case Status.DISCONNECTED:
                sender.stop_notify()
                sender.restart_notify()
            case _:
                pass

    def store_data(self, data: NowData):
        try:
            assert data.location in self.current_data
            assert self.current_data[data.location] == data
            logging.debug(f"no change {data} - {self.current_data}")
        except AssertionError:
            self.current_data[data.location] = data
            Data.create(**data.model_dump(exclude=["timestamp"]))
            logging.debug(data)
            asyncio.run(manager.broadcast(data.model_dump(mode="json")))
            asyncio.run(Lametric.update(data))
            NowdataDb().nowdata(**data.model_dump(mode="json"))