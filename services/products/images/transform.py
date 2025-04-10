
import models
import services.imagek


def transform(product: models.Product, transform: str, image: models.ProductImage = None) -> str:
    """
    """
    if image:
        image_url = image.url
    else:
        image_url = product.image_urls[0]

    if not image_url:
        return ""

    imagekit_root = services.imagek.endpoint()
    return image_url.replace(imagekit_root, f"{imagekit_root}/{transform}")
