import starlette.datastructures

import routers.utils

def test_page_links():
    # page next is valid
    page_prev, page_next = routers.utils.page_links(
        path="/gallery",
        params=starlette.datastructures.QueryParams({
            "offset": 0,
        }),
        limit=10,
        total=11,
    )

    assert page_prev == ""
    assert page_next == "/gallery?offset=10"

    # page next is valid with limit in query
    page_prev, page_next = routers.utils.page_links(
        path="/gallery",
        params=starlette.datastructures.QueryParams({
            "offset": 0,
            "limit": 5,
        }),
        limit=10,
        total=11,
    )

    assert page_prev == ""
    assert page_next == "/gallery?offset=5&limit=5"

    # page next is valid with other query params
    page_prev, page_next = routers.utils.page_links(
        path="/gallery",
        params=starlette.datastructures.QueryParams({
            "offset": 0,
            "name": "foo",
        }),
        limit=10,
        total=11,
    )

    assert page_prev == ""
    assert page_next == "/gallery?offset=10&name=foo"

    # page prev is valid
    page_prev, page_next = routers.utils.page_links(
        path="/gallery",
        params=starlette.datastructures.QueryParams({
            "offset": 10,
        }),
        limit=5,
        total=10,
    )

    assert page_prev == "/gallery?offset=5"
    assert page_next == ""

    # page prev is valid with other query params
    page_prev, page_next = routers.utils.page_links(
        path="/gallery",
        params=starlette.datastructures.QueryParams({
            "offset": 10,
            "name": "foo",
        }),
        limit=5,
        total=10,
    )

    assert page_prev == "/gallery?offset=5&name=foo"
    assert page_next == ""

    # page prev is valid with offset == 0
    page_prev, page_next = routers.utils.page_links(
        path="/gallery",
        params=starlette.datastructures.QueryParams({
            "offset": 10,
        }),
        limit=10,
        total=10,
    )

    assert page_prev == "/gallery"
    assert page_next == ""
