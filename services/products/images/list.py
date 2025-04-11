import dataclasses
import re

import sqlalchemy
import sqlmodel

import models
import services.mql


@dataclasses.dataclass
class Struct:
    code: int
    objects: list[models.ProductImage]
    tags: list[str]
    count: int
    total: int
    errors: list[str]


def list(
    db_session: sqlmodel.Session, query: str = "", offset: int = 0, limit: int = 20, sort: str="id+"
) -> Struct:
    """
    Search product images table
    """
    struct = Struct(
        code=0,
        objects=[],
        tags=[],
        count=0,
        total=0,
        errors=[],
    )

    model = models.ProductImage
    dataset = sqlmodel.select(model)  # default database query

    query_normalized = query

    if query and ":" not in query:
        query_normalized = f"name:{query}"

    struct_tokens = services.mql.parse(query_normalized)

    for token in struct_tokens.tokens:
        value = token["value"]

        if token["field"] == "name":
            # always like query
            value_normal = re.sub(r"~", "", value).lower()
            dataset = dataset.where(
                sqlalchemy.func.lower(model.name).like("%" + value_normal + "%")
            )
        elif token["field"] in ["tags"]:
            values = [s.strip() for s in value.lower().split(",")]
            dataset = dataset.where(model.tags.contains(values))
            struct.tags = values
        elif token["field"] in ["pid", "product_id"]:
            dataset = dataset.where(model.product_id == int(value))

    if sort == "id+":
        dataset = dataset.order_by(model.id.asc())
    else: # defaults to id-
        dataset = dataset.order_by(model.id.desc())

    struct.objects = db_session.exec(dataset.offset(offset).limit(limit)).all()
    struct.count = len(struct.objects)
    struct.total = db_session.scalar(
        sqlmodel.select(sqlalchemy.func.count("*")).select_from(dataset.subquery())
    )

    return struct