import sqlmodel
import ulid

import models
import services.database
import services.products


def test_products_search(db_session: sqlmodel.Session, user_1: models.User):
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

    services.products.update(
        db_session=db_session,
        product=product_1,
        data={},
        brands=["boris saberi"],
        categories=["pants", "trousers"],
        tags=["blue", "orange"],
    )

    # should find product with brand match

    list_result = services.products.list(
        db_session=db_session,
        query="search:boris",
        offset=0,
        limit=10,
    )

    assert list_result.total == 1

    # should find product with category match

    list_result = services.products.list(
        db_session=db_session,
        query="search:pants",
        offset=0,
        limit=10,
    )

    assert list_result.total == 1

    # should find product with tag match

    list_result = services.products.list(
        db_session=db_session,
        query="search:orange",
        offset=0,
        limit=10,
    )

    assert list_result.total == 1

    # should return no products with no matching brand

    list_result = services.products.list(
        db_session=db_session,
        query="search:yuta",
        offset=0,
        limit=10,
    )

    assert list_result.total == 0

    services.database.truncate_tables(db_session=db_session, table_names=["products"])
