import dataclasses


@dataclasses.dataclass
class GrailedListing:
    code: int
    description: str
    image_urls: list[str]
    userid: int
    username: str
    title: str
    errors: list[str]
