import dataclasses
import re

import sqlalchemy
import sqlmodel

import models
import services.mql


@dataclasses.dataclass
class Struct:
    code: int
    objects: list[models.UserAcl]
    count: int
    total: int
    errors: list[str]


def list(
    db_session: sqlmodel.Session, query: str = "", offset: int = 0, limit: int = 20, sort: str="id+"
) -> Struct:
    """
    Search users table
    """
    struct = Struct(
        code=0,
        objects=[],
        count=0,
        total=0,
        errors=[],
    )

    model = models.UserAcl
    dataset = sqlmodel.select(model)  # default database query

    struct_tokens = services.mql.parse(query)

    for token in struct_tokens.tokens:
        value = token["value"]

        if token["field"] in ["id", "ids", "resource_id", "resource_ids"]:
            values = [int(s) for s in value.lower().split(",")]
            dataset = dataset.where(model.resource_id.in_(values))
        elif token["field"] in ["name", "names", "resource_name", "resource_names"]:
            values = [s.strip() for s in value.lower().split(",")]
            dataset = dataset.where(model.resource_name.in_(values))
        elif token["field"] in ["role"]:
            value_normal = re.sub(r"~", "", value).lower()
            dataset = dataset.where(
                sqlalchemy.func.lower(model.roles).like("%" + value_normal + "%")
            )
        elif token["field"] in ["user", "user_id"]:
            dataset = dataset.where(model.user_id == int(value))

    if sort == "id-":
        dataset = dataset.order_by(model.id.desc())
    else: # defaults to id+
        dataset = dataset.order_by(model.id.asc())

    struct.objects = db_session.exec(dataset.offset(offset).limit(limit)).all()
    struct.count = len(struct.objects)
    struct.total = db_session.scalar(
        sqlmodel.select(sqlalchemy.func.count("*")).select_from(dataset.subquery())
    )

    return struct