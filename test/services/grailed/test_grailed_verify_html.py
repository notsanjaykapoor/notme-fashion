import ulid

import services.grailed


def test_grailed_verify_html(mocker):
    mocker.patch("services.grailed.download", return_value=[0, "test/data/grailed_78270192_swrecked.html"])

    # verify with invalid key
    key_invalid = ulid.new().str
    verify_struct = services.grailed.verify(url="https://www.grailed.com/listings/78270192", key=key_invalid)

    assert verify_struct.code == 404
    assert verify_struct.listing.description.startswith("BBS P13TF FKU10002")
    assert verify_struct.listing.username == "swrecked"

    # verify with valid key
    key_valid = "01JRTFK5MCQQKBVRZ62FKCRPXK"
    verify_struct = services.grailed.verify(url="https://www.grailed.com/listings/78270192", key=key_valid)

    assert verify_struct.code == 0
    assert verify_struct.listing.description.startswith("BBS P13TF FKU10002")
    assert verify_struct.listing.username == "swrecked"
