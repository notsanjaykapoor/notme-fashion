import os
import subprocess

import sqlalchemy
import sqlmodel

import dot_init # noqa: F401

database_url = os.environ.get("DATABASE_URL")

assert database_url

connect_args: dict = {}

engine = sqlmodel.create_engine(database_url, echo=False, connect_args=connect_args)


def check(url: str="") -> int:
    """
    returns 0 if database exists; 1 otherwise
    """
    url = url or database_url

    try:
        engine = sqlmodel.create_engine(url, echo=False, connect_args={})
        engine.connect()
        return 0 # database exists
    except Exception:
        return 1


def create(url: str="") -> int:
    """ create database iff it doesn't exist"""
    url = url or database_url

    if check(url) == 0:
        return 0

    url_tokens = url.split("/")
    url_root = "/".join(url_tokens[0:-1])
    db_name = url_tokens[-1]

    psql_cmd = f"psql -d {url_root} -c 'create database {db_name};'"
    subprocess.run(psql_cmd, shell=True)

    return 0


# create and migrate db tables
def migrate():
    sqlmodel.SQLModel.metadata.create_all(engine)


# get session object
def get() -> sqlmodel.Session:
    return sqlmodel.Session(engine)


def table_names() -> list[str]:
    return sqlalchemy.inspect(engine).get_table_names()