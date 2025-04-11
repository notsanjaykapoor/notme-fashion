import datetime
import typing

import sqlalchemy
import sqlalchemy.dialects.postgresql
import sqlmodel

SOURCE_NOTME = "notme"

STATE_ACTIVE = "active"
STATE_DRAFT = "draft"


class Product(sqlmodel.SQLModel, table=True):
    __tablename__ = "products"
    __table_args__ = (
        sqlalchemy.UniqueConstraint("name", name="_products_name"),
        sqlalchemy.UniqueConstraint("source_id", "source_name", name="_source_id_name"),
    )

    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)

    categories: list[str] = sqlmodel.Field(
        default=[],
        sa_column=sqlmodel.Column(sqlalchemy.dialects.postgresql.ARRAY(sqlmodel.String())),
    )
    created_at: datetime.datetime = sqlmodel.Field(
        sa_column=sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), nullable=False),
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
    )
    brands: list[str] = sqlmodel.Field(
        default=[],
        sa_column=sqlmodel.Column(sqlalchemy.dialects.postgresql.ARRAY(sqlmodel.String())),
    )
    data: dict = sqlmodel.Field(
        default_factory=dict, sa_column=sqlmodel.Column(sqlmodel.JSON)
    )
    grailed_id: int = sqlmodel.Field(index=True, nullable=True, default=0)
    image_count: int = sqlmodel.Field(index=True, nullable=True, default=0)
    image_urls: list[str] = sqlmodel.Field(
        default=[],
        sa_column=sqlmodel.Column(sqlalchemy.dialects.postgresql.ARRAY(sqlmodel.String())),
    )
    key: str = sqlmodel.Field(index=True, nullable=False)
    name: str = sqlmodel.Field(index=False, nullable=False)
    notes: str = sqlmodel.Field(
        default="",
        sa_column=sqlmodel.Column(sqlmodel.TEXT),
    )
    source_id: str = sqlmodel.Field(index=True, nullable=False)
    source_name: str = sqlmodel.Field(index=True, nullable=False)
    state: str = sqlmodel.Field(index=True, nullable=True)
    tags: list[str] = sqlmodel.Field(
        default=[],
        sa_column=sqlmodel.Column(sqlalchemy.dialects.postgresql.ARRAY(sqlmodel.String())),
    )
    updated_at: datetime.datetime = sqlmodel.Field(
        sa_column=sqlalchemy.Column(
            sqlalchemy.DateTime(timezone=True),
            nullable=False,
            onupdate=sqlalchemy.sql.func.now(),
        ),
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
    )
    user_id: int = sqlmodel.Field(index=True, nullable=False)


    @property
    def brands_string(self) -> str:
        return ", ".join(self.brands)

    @property
    def categories_string(self) -> str:
        return ", ".join(self.categories)

    @property
    def color(self) -> str:
        return self.data.get("color", "")

    @property
    def grailed_url(self) -> str:
        if self.grailed_id > 0:
            return f"https://www.grailed.com/listings/{self.grailed_id}"

        return ""

    @property
    def material(self) -> str:
        return self.data.get("material", "")

    @property
    def model(self) -> str:
        return self.data.get("model", "")

    @property
    def season(self) -> str:
        return self.data.get("season", "")

    @property
    def size(self) -> str:
        return self.data.get("size", "")

    @property
    def tags_string(self) -> str:
        return ", ".join(self.tags)