from termos.sensor.models import SensorType
from termos.sensor.oria import Oria
from termos.sensor.sensor import SensorMeta
from termos.sensor.tp357 import TP357
from termos.sensor.http import HTTP


def get_sensor_type_class(sensor_type: SensorMeta):
    
    match sensor_type:
        case SensorType.TP357:
            return TP357
        case SensorType.ORIA:
            return Oria
        case SensorType.HTTP:
            return HTTP
        case _:
            raise NotImplementedError