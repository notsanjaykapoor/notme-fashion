import hashlib
import secrets

import imagekitio.models.UploadFileRequestOptions
import sqlmodel

import models
import services.files
import services.imagek
import services.products.images

def create(
    db_session: sqlmodel.Session,
    product: models.Product,
    folder: str,
    url: str,
) -> tuple[int, models.ProductImage | None]:
    """
    Upload image, and persist product image to database
    """

    # generate fingerprint and check if image exists

    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()

    list_result = services.products.images.list(db_session=db_session, query=f"product_id:{product.id}")
    product_images = list_result.objects

    for product_image in product_images:
        if product_image.fingerprint == url_hash:
            return 409, product_image

    options = imagekitio.models.UploadFileRequestOptions.UploadFileRequestOptions(
        custom_metadata = {
            "product_id": product.id,
        },
        is_private_file=False,
        folder=folder,
        overwrite_file=False,
        use_unique_file_name=False,
    )

    client = services.imagek.client()

    # upload image url or file

    path, _, _ = services.files.file_uri_parse(source_uri=url)

    if path:
        # read file
        url_file = open(path, "rb")
    else:
        # use url
        url_file = url

    image_key = secrets.token_hex(3)
    image_name = f"product-{product.key}-{image_key}"

    result = client.upload(
        file=url_file,
        file_name=image_name,
        options=options
    )

    # create product_image object

    raw_data = result.response_metadata.raw
    image_name = raw_data.get("name")
    image_url = raw_data.get("url")

    product_image = models.ProductImage(
        data=raw_data,
        fingerprint=url_hash,
        name=image_name,
        product_id=product.id,
        url=image_url,
    )

    db_session.add(product_image)
    db_session.commit()

    return 0, product_image
