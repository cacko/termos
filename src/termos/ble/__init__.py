from termos.ble.models import SensorType
from termos.ble.oria import Oria
from termos.ble.sensor import SensorMeta
from termos.ble.tp357 import TP357


def get_sensor_type_class(sensor_type: SensorMeta):
    
    match sensor_type:
        case SensorType.TP357:
            return TP357
        case SensorType.ORIA:
            return Oria
        case _:
            raise NotImplementedError