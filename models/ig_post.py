import dataclasses


@dataclasses.dataclass
class IgPost:
    code: int
    description: str
    userid: int
    username: str
    title: str
    errors: list[str]
