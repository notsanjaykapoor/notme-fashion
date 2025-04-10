import dataclasses
import re

import sqlalchemy
import sqlmodel

import models
import services.mql


@dataclasses.dataclass
class Struct:
    code: int
    objects: list[models.Product]
    cateories: list[str]
    tags: list[str]
    count: int
    total: int
    errors: list[str]


def list(
    db_session: sqlmodel.Session, query: str = "", offset: int = 0, limit: int = 20, scope: str="", sort: str="id+"
) -> Struct:
    """
    Search products table
    """
    struct = Struct(
        code=0,
        objects=[],
        cateories=[],
        tags=[],
        count=0,
        total=0,
        errors=[],
    )

    model = models.Product
    dataset = sqlmodel.select(model)  # default database query

    query_normalized = query

    if query and ":" not in query:
        query_normalized = f"name:{query}"

    if scope:
        query_normalized = f"{query_normalized} {scope}".strip()

    struct_tokens = services.mql.parse(query_normalized)

    for token in struct_tokens.tokens:
        value = token["value"]

        if token["field"] in ["category", "categories"]:
            values = [s.strip() for s in value.lower().split(",")]
            dataset = dataset.where(model.categories.contains(values))
            struct.categories = values
        elif token["field"] == "grailed":
            if int(value) == 1:
                dataset = dataset.where(model.grailed_id > 0)
            else:
                dataset = dataset.where(model.grailed_id == 0)
        elif token["field"] == "key":
            dataset = dataset.where(model.key == value)
        elif token["field"] == "name":
            # always like query
            value_normal = re.sub(r"~", "", value).lower()
            dataset = dataset.where(
                sqlalchemy.func.lower(model.name).like("%" + value_normal + "%")
            )
        elif token["field"] in ["source", "source_name"]:
            dataset = dataset.where(model.source_name == value)
        elif token["field"] in ["state"]:
            dataset = dataset.where(model.state == value)
        elif token["field"] in ["tags"]:
            values = [s.strip() for s in value.lower().split(",")]
            dataset = dataset.where(model.tags.contains(values))
            struct.tags = values
        elif token["field"] in ["uid", "user_id"]:
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