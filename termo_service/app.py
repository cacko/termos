from ast import Or
import asyncio
import logging
from time import sleep
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from termo_service.api.router import router as api_router
from termo_service.ble.models import SensorLocation
from termo_service.ws.router import router as ws_router, manager
from termo_service.ble.tp357 import TP357
from termo_service.ble.oria import Oria
from termo_service.server import Server
from contextlib import asynccontextmanager
import signal
import sys
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
TP357.location = SensorLocation.INDOOR
TP357.register(server.queue)
Oria.location = SensorLocation.OUTDOOR
Oria.register(server.queue)

@asynccontextmanager
async def lifespan(app: FastAPI):
    server.start()
    TP357.start_notify()
    Oria.start_notify()
    yield
    logging.info("lifespan")


def create_app():
    
    origins = [
        "http://localhost:4200",
        "https://termo.cacko.net",
        "https://termo-4737a.web.app",
        "https://termo-4737a.firebaseapp.com",
    ]
    
    app = FastAPI(
        title="termo@cacko.net",
        lifespan=lifespan
    )
    
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
    TP357.stop()
    Oria.stop()
    sleep(1)
    shutdown(PID)

signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)

