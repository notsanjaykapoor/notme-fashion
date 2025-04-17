import pytest
import sqlalchemy.exc
import sqlmodel
import ulid

import models
import services.database
import services.products


def test_products_create(db_session: sqlmodel.Session, user_1: models.User):
    # create valid product
    ulid_1 = ulid.new().str

    product_1 = services.products.create(
        db_session=db_session,
        key=ulid.new().str,
        name="Product 1",
        source_id=ulid_1,
        source_name=models.product.SOURCE_NOTME,
        state=models.product.STATE_ACTIVE,
        user_id=user_1.id,
    )

    assert product_1.id
    assert product_1.brands == []
    assert product_1.categories == []
    assert product_1.grailed_id == 0
    assert product_1.key
    assert product_1.links == []
    assert product_1.name == "Product 1"
    assert product_1.search_vector
    assert product_1.source_id
    assert product_1.source_name == "notme"
    assert product_1.state == "active"
    assert product_1.tags == []
    assert product_1.user_id == user_1.id

    with pytest.raises(sqlalchemy.exc.IntegrityError):
        # source should be unique
        services.products.create(
            db_session=db_session,
            key=ulid.new().str,
            name="Random name",
            source_id=ulid_1,
            source_name=models.product.SOURCE_NOTME,
            state=models.product.STATE_ACTIVE,
            user_id=user_1.id,
        )

    db_session.rollback()

    services.database.truncate_tables(db_session=db_session, table_names=["products"])

