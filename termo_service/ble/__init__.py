from termo_service.ble.models import SensorType
from termo_service.ble.oria import Oria
from termo_service.ble.sensor import SensorMeta
from termo_service.ble.tp357 import TP357


def get_sensor_type_class(sensor_type: SensorMeta):
    
    match sensor_type:
        case SensorType.TP357:
            return TP357
        case SensorType.ORIA:
            return Oria
        case _:
            raise NotImplementedError