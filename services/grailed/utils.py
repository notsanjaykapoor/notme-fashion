import dataclasses
import re

@dataclasses.dataclass
class GrailedUrl:
    id: int
    url: str



def listing_url(id: int) -> str:
    return f"https://www.grailed.com/listings/{id}"


def listing_url_match(url: str) -> GrailedUrl | None:
    match = re.search(r"^https://www.grailed.com/listings/(\d+)", url) or re.search(r"^grailed:(\d+)", url)

    if not match:
        return None

    return GrailedUrl(
        id=int(match[1]),
        url=url,
    )