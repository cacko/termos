from typing import Optional
import yaml
from pydantic import BaseModel
from pathlib import Path
from stringcase import camelcase
from termo_service.ble.models import SensorLocation, SensorType


class LametricEndPointConfig(BaseModel):
    nowdata: str


class LametricConfig(BaseModel):
    headers: dict[str, str]
    base_url: str
    endpoints: LametricEndPointConfig


class FirebaseConfig(BaseModel):
    admin_json: str
    rdb_host: str


class BleDeviceConfig(BaseModel):
    mac: str
    address: str
    uuid_read: str
    uuid_write: str
    sensor_type: SensorType
    location: SensorLocation
    
    @property
    def class_name(self):
        return f"{self.sensor_type}{camelcase(self.address)}"
    
    
class DbConfig(BaseModel):
    name: str
    username: str
    host: str


class AppConfig(BaseModel):
    lametric: LametricConfig
    firebase: FirebaseConfig
    devices: list[BleDeviceConfig]
    db: DbConfig


config_root = Path(__file__).parent / "settings.yaml"
data = yaml.full_load(config_root.read_text())

app_config = AppConfig(**data)
