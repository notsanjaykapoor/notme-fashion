import hashlib

import sqlmodel

import models
import services.imagek
import services.products.images


def delete(
    db_session: sqlmodel.Session,
    product: models.Product,
    image: models.ProductImage,
) -> int:
    """
    Delete image from imagekit and then from database.
    """

    client = services.imagek.client()

    _result = client.delete_file(file_id=image.data_file_id)

    db_session.delete(image)
    db_session.commit()

    return 0
