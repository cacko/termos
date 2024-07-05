import logging
from time import sleep
from playhouse.postgres_ext import PostgresqlExtDatabase
from typing import Optional, Any
from peewee import OperationalError
from termo_service.config import app_config

class ReconnectingDB(PostgresqlExtDatabase):
    
    def execute_sql(self, sql, params: Any | None = ..., commit=...):
        try:
            sleep(6)
            return super().execute_sql(sql, params, commit)
        except OperationalError as e:
            logging.error(e)


class DatabaseMeta(type):
    _instance: Optional['Database'] = None

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
        print(cfg)
        self.__db = ReconnectingDB(
            cfg.name,
            user=cfg.username,
            hostaddr=cfg.host,
            sslmode="disable"
        )

    def get_db(self) -> ReconnectingDB:
        return self.__db
