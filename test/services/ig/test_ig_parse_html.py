import services.ig

def test_parse_html():
    post_struct = services.ig.parse_html("test/data/insta_DGDzftUquYL_swrecked.html")

    assert post_struct.code == 0
    assert post_struct.title == "Sanjay Kapoor on Instagram: \"#paris #freddys\""
    assert post_struct.userid == 0
    assert post_struct.username == "swrecked"
