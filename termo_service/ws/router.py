from enum import StrEnum
from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)
import logging
from fastapi.websockets import WebSocketState
from pydantic import BaseModel, Field
from typing import Optional
from pathlib import Path
import asyncio
import time
from asyncio.queues import Queue, QueueEmpty

from termo_service.ble.models import NowData, SensorLocation
from termo_service.db.models.data import Data


router = APIRouter()

N_WORKERS = 4


class ConnectionManager:

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    def get_last_nowdata(self, location: SensorLocation) -> NowData:
        return NowData(**Data.get_last_data(location=location).model_dump())

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        await websocket.send_json(
            self.get_last_nowdata(location=SensorLocation.INDOOR).model_dump(
                mode="json"
            )
        )
        await websocket.send_json(
            self.get_last_nowdata(location=SensorLocation.OUTDOOR).model_dump(
                mode="json"
            )
        )

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def shutdown(self):
        for connection in self.active_connections:
            await connection.close()
            self.disconnect(connection)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                assert connection.client_state == WebSocketState.CONNECTED
                await connection.send_json(message)
            except AssertionError:
                self.disconnect(connection)


manager = ConnectionManager()


@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    queue: Queue = Queue()

    async def read_from_socket(websocket: WebSocket):
        async for data in websocket.iter_json():
            queue.put_nowait(data)

    async def get_data_and_send(n: int):
        while True:
            try:
                data = queue.get_nowait()
                logging.debug(f"WORKER #{n}, {data}")
                queue.task_done()
            except QueueEmpty:
                await asyncio.sleep(0.2)
            except WebSocketDisconnect:
                logging.debug(f"DISCONNECT {websocket}")
                manager.disconnect(websocket)
                break
            except Exception as e:
                logging.exception(e)

    await asyncio.gather(
        read_from_socket(websocket),
        *[asyncio.create_task(get_data_and_send(n)) for n in range(1, N_WORKERS + 1)],
    )
