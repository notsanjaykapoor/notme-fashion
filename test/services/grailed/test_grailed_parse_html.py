import services.grailed

def test_grailed_parse_html():
    listing_struct = services.grailed.parse_html("test/data/grailed_77057038_swrecked.html")

    assert listing_struct.code == 0
    assert listing_struct.description.startswith("BBS P13TF F1939")
    assert listing_struct.image_urls == [
        "https://media-assets.grailed.com/prd/listing/temp/3c1973c9df6343d5af145f8f6e0c64fd",
        "https://media-assets.grailed.com/prd/listing/temp/965e6a9e8637417395804c200f61f4ca",
        "https://media-assets.grailed.com/prd/listing/temp/ce3fdacd9a114ccfb101895bcbd8e1dc",
        "https://media-assets.grailed.com/prd/listing/temp/5932a8e92e364afda04a4bb920f339f5",

    ]
    assert listing_struct.title == "SS19 P13TF F1939 Boris Saberi Light Grey Pants"
    assert listing_struct.userid == 833830
    assert listing_struct.username == "swrecked"
