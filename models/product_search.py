import dataclasses


@dataclasses.dataclass
class ProductSearch:
    name: str
    query: str
