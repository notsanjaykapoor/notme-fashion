import typing

import sqlalchemy
import sqlmodel


class ProductImage(sqlmodel.SQLModel, table=True):
    __tablename__ = "product_images"
    __table_args__ = (
        sqlalchemy.UniqueConstraint("name", name="_product_image_name"),
        sqlalchemy.UniqueConstraint("url", name="_product_image_url"),
    )

    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)

    data: dict = sqlmodel.Field(
        default_factory=dict, sa_column=sqlmodel.Column(sqlmodel.JSON)
    )
    name: str = sqlmodel.Field(index=False, nullable=False)
    fingerprint: str = sqlmodel.Field(index=False, nullable=False)
    position: int = sqlmodel.Field(default=0, nullable=False)
    product_id: int = sqlmodel.Field(index=True, nullable=False)
    url: str = sqlmodel.Field(index=False, nullable=False)
