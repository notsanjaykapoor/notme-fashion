import os

import imagekitio


def client():
    """
    Return imagekit client.
    """
    return imagekitio.ImageKit(
        private_key=os.environ.get("IMAGEKIT_PRIVATE_KEY"),
        public_key=os.environ.get("IMAGEKIT_PUBLIC_KEY"),
        url_endpoint=os.environ.get("IMAGEKIT_ENDPOINT"),
    )

def endpoint() -> str:
    """
    """
    return os.environ.get("IMAGEKIT_ENDPOINT")