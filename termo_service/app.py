import logging
from time import sleep
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import rich
from termo_service.api.router import router as api_router
from termo_service.ble import get_sensor_type_class
from termo_service.ble.models import SensorLocation, SensorType
from termo_service.ws.router import router as ws_router
from termo_service.ble.sensor import Sensor, SensorMeta
from termo_service.server import Server
from termo_service.config import app_config
from contextlib import asynccontextmanager
import signal
import os
import psutil


PID = os.getpid()


def shutdown(pid, including_parent=True):
    try:
        parent = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return
    children = parent.children(recursive=True)
    for child in children:
        logging.warning(f"killing child {child}")
        child.kill()
    psutil.wait_procs(children, timeout=5)
    if including_parent:
        logging.warning(f"killing parent {pid}")
        parent.kill()
        parent.wait(5)


server = Server()
sensors: list[SensorMeta] = []

for dc in app_config.devices:
    inst: SensorMeta = type(dc.class_name, (get_sensor_type_class(dc.sensor_type),), dc.model_dump())
    inst.register(
        ui_queue=server.queue,
    )
    sensors.append(inst)

@asynccontextmanager
async def lifespan(app: FastAPI):
    server.start()
    for sensor in sensors:
        sensor.start_notify()
    yield
    raise RuntimeError


def create_app():

    origins = [
        "http://localhost:4200",
        "https://termo.cacko.net",
        "https://termo-4737a.web.app",
        "https://termo-4737a.firebaseapp.com",
    ]

    app = FastAPI(title="termo@cacko.net", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["x-pagination-page", "x-pagination-total", "x-pagination-next"],
    )

    app.include_router(api_router, prefix="/api")
    app.include_router(ws_router, prefix="/ws")
    return app


def handler_stop_signals(signum, frame):
    server.stop()
    sleep(1)
    for sensor in sensors:
        sensor.stop()
    sleep(1)
    shutdown(PID)


signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)
