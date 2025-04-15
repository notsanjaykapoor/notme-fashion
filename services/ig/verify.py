import dataclasses

import models


@dataclasses.dataclass
class Struct:
    code: int
    post: models.IgPost 
    errors: list[str]


def verify(url: str, key: str) -> Struct:
    """
    """
    struct = Struct(
        code=0,
        post=None,
        errors=[]
    )

    return struct
