import datetime
import typing

import sqlalchemy
import sqlmodel


IDP_GOOGLE = "google"
IDP_PASS = "pass"

STATE_ACTIVE = "active"

TZ_DEFAULT = "US/Chicago"


class User(sqlmodel.SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = (sqlalchemy.UniqueConstraint("email", name="_users_email"),)

    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)

    created_at: datetime.datetime = sqlmodel.Field(
        sa_column=sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), nullable=False),
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
    )
    data: dict = sqlmodel.Field(
        default_factory=dict, sa_column=sqlmodel.Column(sqlmodel.JSON)
    )
    email: str = sqlmodel.Field(index=True, nullable=False)
    grailed_handle: str = sqlmodel.Field(index=True, nullable=True)
    handle: str = sqlmodel.Field(index=True, nullable=False)
    ig_handle: str = sqlmodel.Field(index=True, nullable=True)
    idp: str = sqlmodel.Field(index=True, nullable=False)
    name: str = sqlmodel.Field(index=False, nullable=True)
    state: str = sqlmodel.Field(index=True, nullable=False)
    tz: str = sqlmodel.Field(index=False, nullable=True, default="")
    updated_at: datetime.datetime = sqlmodel.Field(
        sa_column=sqlalchemy.Column(
            sqlalchemy.DateTime(timezone=True),
            nullable=False,
            onupdate=sqlalchemy.sql.func.now(),
        ),
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
    )