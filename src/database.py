import time
from functools import wraps
from decouple import config
import pymysql

config_db = {
    "host": config("MYSQL_HOST"),
    "port": config("MYSQL_PORT", cast=int),
    "db": config("MYSQL_DATABASE"),
    "user": config("MYSQL_USER"),
    "password": config("MYSQL_PASSWORD")
}

def with_connection(function):
    @wraps(function)
    def _with_connection(*args, **kwargs):
        with pymysql.Connect(**config_db) as connection:
            try:
                return function(connection, *args, **kwargs) 
            except pymysql.err.OperationalError as err:
                print(err)
                time.sleep(1)
    return _with_connection
