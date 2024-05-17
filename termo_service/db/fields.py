from peewee import CharField
from termo_service.ble.models import SensorLocation


class LocationField(CharField):

    def db_value(self, value: SensorLocation):
        return value.value

    def python_value(self, value):
        return SensorLocation(value)
