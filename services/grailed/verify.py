import dataclasses

import models
import services.grailed


@dataclasses.dataclass
class Struct:
    code: int
    listing: models.GrailedListing 
    errors: list[str]


def verify(url: str, key: str) -> Struct:
    """
    Verify grailed listing url contains the specified key.
    """
    struct = Struct(
        code=0,
        listing=None,
        errors=[]
    )

    grailed_url = services.grailed.listing_url_match(url=url)

    if not grailed_url:
        struct.code = 422
        struct.errors.append("grailed url is invalid")
        return struct

    code, html_path = services.grailed.download(grailed_id=grailed_url.id, overwrite=0)

    # code, html_path = [0, f"grailed_{grailed_url.id}.html"]

    if code not in [0, 409]:
        struct.code = 500
        struct.errors.append(f"grailed listing download error code {code}")
        return struct

    struct.listing = services.grailed.parse_html(html_path=html_path)

    text_compare = struct.listing.description

    if key not in text_compare:
        struct.code = 404
        struct.errors.append(f"grailed listing missing key '{key}'")
        return struct
    
    return struct
