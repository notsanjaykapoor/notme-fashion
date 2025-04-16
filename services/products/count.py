import sqlalchemy
import sqlmodel

import models


def count(db_session: sqlmodel.Session) -> int:
    count = db_session.scalar(
        sqlmodel.select(sqlalchemy.func.count(models.Product.id))
    )

    return count
