import typing

import sqlmodel

import models


def get_by_id(db_session: sqlmodel.Session, id: int) -> typing.Optional[models.Product]:
    """ """
    db_select = sqlmodel.select(models.Product).where(models.Product.id == id)
    db_object = db_session.exec(db_select).first()

    return db_object


def get_by_name(db_session: sqlmodel.Session, name: str) -> typing.Optional[models.Product]:
    """ """
    db_select = sqlmodel.select(models.Product).where(models.Product.name == name)
    db_object = db_session.exec(db_select).first()

    return db_object


def get_by_source(db_session: sqlmodel.Session, source_id: str, source_name: str) -> typing.Optional[models.Product]:
    """ """
    db_select = sqlmodel.select(models.Product).where(models.Product.source_id == source_id).where(models.Product.source_name == source_name)
    db_object = db_session.exec(db_select).first()

    return db_object