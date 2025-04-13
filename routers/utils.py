import os

import starlette.datastructures


def page_links(path: str, params: starlette.datastructures, limit: int, total: int) -> tuple[str, str]:
    """
    Generate next and previous page links from the current url request.
    """
    offset = int(params._dict.get("offset", 0))
    limit = int(params._dict.get("limit", limit))

    page_prev = ""
    page_next = ""

    if offset + limit < total:
        next_dict = params._dict.copy()
        next_dict["offset"] = offset+limit
        next_params = starlette.datastructures.QueryParams(next_dict)
        page_next = f"{path}?{str(next_params)}"

    if offset - limit >= 0:
        prev_dict = params._dict.copy()
        if offset - limit > 0:
            prev_dict["offset"] = offset-limit
        else:
            prev_dict.pop("offset", 0)

        if prev_dict:
            prev_params = starlette.datastructures.QueryParams(prev_dict)
            page_prev = f"{path}?{str(prev_params)}"
        else:
            page_prev = path

    return page_prev, page_next