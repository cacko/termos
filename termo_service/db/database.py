from peewee import PostgresqlDatabase
from playhouse.shortcuts import ReconnectMixin, OperationalError, InterfaceError
from typing import Optional
from termo_service.config import app_config


class ReconnectingDB(ReconnectMixin, PostgresqlDatabase):

    reconnect_errors = (
        (OperationalError, "terminat"),
        (InterfaceError, "connection already closed"),
    )


class DatabaseMeta(type):
    _instance: Optional["Database"] = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = type.__call__(cls, *args, **kwargs)
        return cls._instance

    @property
    def db(cls) -> ReconnectingDB:
        return cls().get_db()


class Database(object, metaclass=DatabaseMeta):

    def __init__(self):
        cfg = app_config.db
        self.__db = ReconnectingDB(
            cfg.name, user=cfg.username, hostaddr=cfg.host, sslmode="disable"
        )

    def get_db(self) -> ReconnectingDB:
        return self.__db
