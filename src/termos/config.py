import os
import yaml
from pydantic import BaseModel, constr
from pathlib import Path
from stringcase import camelcase
from termos.ble.models import SensorLocation, SensorType
from pathlib import Path
from appdirs import user_data_dir, user_config_dir
from termos import __name__

DATA_DIR = Path(user_data_dir(__name__))
CONFIG_DIR = Path(user_config_dir(__name__))

if not DATA_DIR.exists():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    

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
    mac: constr(to_upper=True)
    address: constr(to_upper=True)
    uuid_read: str
    uuid_write: str
    sensor_type: SensorType
    location: SensorLocation
    
    @property
    def class_name(self):
        return f"{self.sensor_type}{camelcase(self.address)}"
    
    
class DbConfig(BaseModel):
    url: str


class AppConfig(BaseModel):
    lametric: LametricConfig
    firebase: FirebaseConfig
    devices: list[BleDeviceConfig]
    db: DbConfig


config_root = os.environ.get("TERMOS_SETTINGS", CONFIG_DIR / "settings.yaml")
data = yaml.full_load(config_root.read_text())

app_config = AppConfig(**data)
