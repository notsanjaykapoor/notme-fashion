import sqlmodel

import models
import services.imagek
import services.products.images


def sync_versions(db_session: sqlmodel.Session, product: models.Product) -> int:
    """
    Sync imagekit image version data with local db.
    """
    list_result = services.products.images.list(db_session=db_session, query=f"product_id:{product.id}")
    images_list = list_result.objects

    client = services.imagek.client()

    for image in images_list:
        versions_results = client.get_file_versions(file_id=image.data.get("fileId"))
        image_version_url = versions_results.list[0].url

        if image_version_url != image.url:
            image.url = image_version_url
            db_session.add(image)
            db_session.commit()

    return 0
