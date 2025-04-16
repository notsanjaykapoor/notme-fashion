import sqlalchemy.orm.attributes
import sqlalchemy.sql
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
) -> int:
    """
    Sync product search_vector field which is derived from other product fields.
    """
    product.search_vector = sqlalchemy.sql.func.to_tsvector(product.search_text)

    db_session.add(product)
    db_session.commit()

    return 0