import sqlalchemy.orm.attributes
import sqlmodel

import models
import services.products.images


def sync_images(db_session: sqlmodel.Session, product: models.Product) -> int:
    """
    Sync image versions and urls
    """
    services.products.images.sync_versions(
        db_session=db_session,
        product=product,
    )

    list_result = services.products.images.list(db_session=db_session, query=f"product_id:{product.id}", sort="id+")
    images_list = list_result.objects
    image_urls = [product_image.url for product_image in images_list]

    if product.image_urls != image_urls:
        product.image_urls = image_urls
        product.image_count = len(image_urls)

        db_session.add(product)
        db_session.commit()

    return 0


def sync_meta(
    db_session: sqlmodel.Session,
    product: models.Product,
    data: dict,
    brands: list[str]=[],
    categories: list[str]=[],
    tags: list[str]=[],
) -> int:
    """
    Sync product metadata.
    """
    if brands and product.brands != sorted(brands):
        product.brands = sorted(brands)

    if categories and product.categories != sorted(categories):
        product.categories = sorted(categories)

    if tags and product.tags != sorted(tags):
        product.tags = sorted(tags)

    data_mod = product.data
    data_changes = 0

    for key, value in data.items():
        if key not in data_mod or data_mod.get(key) != value:
            data_mod[key] = value
            data_changes += 1

    if data_changes > 0:
        product.data = data_mod
        sqlalchemy.orm.attributes.flag_modified(product, "data")

    db_session.add(product)
    db_session.commit()

    return 0