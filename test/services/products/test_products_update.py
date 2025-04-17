import sqlmodel
import ulid

import models
import services.database
import services.products


def test_products_updates(db_session: sqlmodel.Session, user_1: models.User):
    # create valid product

    product_1 = services.products.create(
        db_session=db_session,
        key=ulid.new().str,
        name="Product 1",
        source_id=ulid.new().str,
        source_name=models.product.SOURCE_NOTME,
        state=models.product.STATE_ACTIVE,
        user_id=user_1.id,
    )

    assert product_1.id
    assert services.products.count(db_session=db_session) == 1

    # should add brand

    assert product_1.brands == []

    services.products.update(
        db_session=db_session,
        product=product_1,
        data={},
        brands=["jas", "ma+"],
    )

    product_1 = services.products.get_by_id(db_session=db_session, id=product_1.id)

    assert product_1.brands == ["jas", "ma+"]

    # should remove brand

    services.products.update(
        db_session=db_session,
        product=product_1,
        data={},
        brands=["jas"],
    )

    product_1 = services.products.get_by_id(db_session=db_session, id=product_1.id)

    assert product_1.brands == ["jas"]

    # should add link

    assert product_1.links == []

    services.products.update(
        db_session=db_session,
        product=product_1,
        data={},
        links=["https://www.fashion.com"],
    )

    product_1 = services.products.get_by_id(db_session=db_session, id=product_1.id)

    assert product_1.links == ["https://www.fashion.com"]

    services.database.truncate_tables(db_session=db_session, table_names=["products"])
