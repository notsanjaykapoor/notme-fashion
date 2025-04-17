import dataclasses
import re
import time

import sqlalchemy
import sqlmodel

import models
import services.mql


@dataclasses.dataclass
class Struct:
    code: int
    objects: list[models.Product]
    brands: list[str]
    categories: list[str]
    tags: list[str]
    count: int
    total: int
    msec: int
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
        brands=[],
        categories=[],
        tags=[],
        count=0,
        total=0,
        msec=0,
        errors=[],
    )

    model = models.Product
    dataset = sqlmodel.select(model)  # default database query

    query_normalized = query

    if query and ":" not in query:
        query_normalized = f"search:{query}"

    if scope:
        query_normalized = f"{query_normalized} {scope}".strip()

    struct_tokens = services.mql.parse(query_normalized)

    t_start_unix = time.time()

    for token in struct_tokens.tokens:
        value = token["value"]

        if token["field"] in ["brand", "brands"]:
            values = [s.strip() for s in value.lower().split(",")]
            dataset = dataset.where(model.brands.contains(values))
            struct.brands = values
        elif token["field"] == "color":
            dataset = dataset.where(model.data["color"].as_string().like("%" + value + "%"))
        elif token["field"] in ["category", "categories"]:
            values = [s.strip() for s in value.lower().split(",")]
            dataset = dataset.where(model.categories.contains(values))
            struct.categories = values
        elif token["field"] == "grailed":
            if int(value) == 1:
                dataset = dataset.where(model.grailed_id > 0)
            else:
                dataset = dataset.where(model.grailed_id == 0)
        elif token["field"] in ["id", "ids"]:
            values = [int(s) for s in value.lower().split(",")]
            dataset = dataset.where(model.id.in_(values))
        elif token["field"] in ["images"]:
            if int(value) == 0:
                dataset = dataset.where(model.image_count == 0)
            else:
                dataset = dataset.where(model.image_count >= int(value))
        elif token["field"] == "key":
            dataset = dataset.where(model.key == value)
        elif token["field"] in ["links"]:
            if int(value) == 0:
                dataset = dataset.where(sqlalchemy.sql.func.cardinality(model.links) == 0)
            else:
                dataset = dataset.where(sqlalchemy.sql.func.cardinality(model.links) >= int(value))
        elif token["field"] == "material":
            dataset = dataset.where(model.data["material"].as_string().like("%" + value + "%"))
        elif token["field"] == "name":
            # always like query
            value_normal = re.sub(r"~", "", value).lower()
            dataset = dataset.where(
                sqlalchemy.func.lower(model.name).like("%" + value_normal + "%")
            )
        elif token["field"] == "search":
            dataset = dataset.where(model.search_vector.match(value))
        elif token["field"] == "season":
            dataset = dataset.where(model.data["season"].as_string().like("%" + value + "%"))
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

    struct.msec = round((time.time() - t_start_unix) * 1000, 2)

    return struct