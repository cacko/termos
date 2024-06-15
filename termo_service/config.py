import yaml
from pydantic import BaseModel
from pathlib import Path


class LametricEndPointConfig(BaseModel):
    nowdata: str


class LametricConfig(BaseModel):
    headers: dict[str, str]
    base_url: str
    endpoints: LametricEndPointConfig


class FirebaseConfig(BaseModel):
    admin_json: str
    rdb_host: str


class BleConfig(BaseModel):
    mac: str
    address: str
    uuid_read: str
    uuid_write: str
    
class BleDevices(BaseModel):
    tp357: BleConfig
    oria: BleConfig
    
class DbConfig(BaseModel):
    url: str


class AppConfig(BaseModel):
    lametric: LametricConfig
    firebase: FirebaseConfig
    ble: BleDevices
    db: DbConfig


config_root = Path(__file__).parent / "settings.yaml"
data = yaml.full_load(config_root.read_text())

app_config = AppConfig(**data)
