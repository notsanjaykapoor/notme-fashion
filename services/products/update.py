import sqlalchemy
import sqlmodel

import models


def update(
    db_session: sqlmodel.Session,
    product: models.Product,
    data: dict,
    brands: list[str]=[],
    categories: list[str]=[],
    links: list[str]=[],
    tags: list[str]=[],
) -> int:
    """
    Update product.

    This includes
      - updating brands, categories, and tags fields
      - updating product data 'metadata' field
      - updating search_vector field which is derived from other product data fields
    """
    if brands and product.brands != sorted(brands):
        product.brands = sorted(brands)

    if categories and product.categories != sorted(categories):
        product.categories = sorted(categories)

    if links and product.links != sorted(links):
        product.links = [s.strip() for s in sorted(set(product.links).union(links))]

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

    product.search_vector = sqlalchemy.sql.func.to_tsvector(product.search_text)

    db_session.add(product)
    db_session.commit()

    return 0