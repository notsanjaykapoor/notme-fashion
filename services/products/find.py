import dataclasses

import sqlmodel

import models
import services.products


@dataclasses.dataclass
class Struct:
    code: int
    objects: list[models.Product]
    query: str
    errors: list[str]


def find_by_queries(db_session: sqlmodel.Session, queries: list[str]) -> Struct:
    """
    Find unique product using the first query that produces a unique result.
    """
    struct = Struct(
        code=0,
        objects=[],
        query="",
        errors=[],
    )

    for query in queries:
        list_result = services.products.list(
            db_session=db_session,
            query=query,
            offset=0,
            limit=5
        )

        struct.query = query
        struct.objects = list_result.objects

        if len(list_result.objects) == 1:
            return struct

    if len(list_result.objects) == 0:
        struct.code = 404
    else:
        struct.code = 422

    return struct
