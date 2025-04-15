import services.grailed

def test_listing_urls():
    # valid url
    grailed_url = services.grailed.listing_url_match(url="https://www.grailed.com/listings/123456789-shirt")

    assert grailed_url.id == 123456789

    # valid shorthand
    grailed_url = services.grailed.listing_url_match(url="grailed:123456789")

    assert grailed_url.id == 123456789

    # invalid url
    grailed_url = services.grailed.listing_url_match(url="https://google.com")

    assert grailed_url == None