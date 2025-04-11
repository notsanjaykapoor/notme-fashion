import typing

import sqlmodel

import models


def create(
    db_session: sqlmodel.Session,
    key: str,
    name: str,
    source_id: str,
    source_name: str,
    state: str,
    user_id: int,
    grailed_id: int=0,
) -> typing.Optional[models.Product]:
    """
    Create product and persist to database
    """

    product = models.Product(
        grailed_id=grailed_id,
        key=key,
        name=name.strip(),
        source_id=source_id,
        source_name=source_name,
        state=state,
        user_id=user_id,
    )

    db_session.add(product)
    db_session.commit()

    return product


