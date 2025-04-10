import typing

import sqlmodel

import models


def get_by_email(db_session: sqlmodel.Session, email: str) -> typing.Optional[models.User]:
    """ """
    db_select = sqlmodel.select(models.User).where(models.User.email == email)
    db_object = db_session.exec(db_select).first()

    return db_object


def get_by_id(db_session: sqlmodel.Session, id: int) -> typing.Optional[models.User]:
    """ """
    db_select = sqlmodel.select(models.User).where(models.User.id == id)
    db_object = db_session.exec(db_select).first()

    return db_object