from .database import Database
from .models.data import Data


def create_tables(drop=False):
    tables = [
        Data
    ]
    if drop:
        Database.db.drop_tables(tables)
    Database.db.create_tables(tables)

