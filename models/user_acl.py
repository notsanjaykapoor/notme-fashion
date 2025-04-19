import datetime
import typing

import sqlalchemy
import sqlmodel


# NAME_MAPS = {
#     "super": "r:users id:0 role:m",
# }

RESOURCE_PRODUCTS = "products"
RESOURCE_USERS = "users"

RESOURCES = [
    RESOURCE_PRODUCTS,
    RESOURCE_USERS,
]

# represents manage, read, write
ROLES_ALL = "mrw"
ROLES_MANAGE = "m"
ROLES_READ = "r"
ROLES_WRITE = "w"


class UserAcl(sqlmodel.SQLModel, table=True):
    __tablename__ = "user_acls"
    __table_args__ = (
        sqlalchemy.UniqueConstraint("resource_name", "resource_id", "user_id", name="_resource_user"),
    )

    id: typing.Optional[int] = sqlmodel.Field(default=None, primary_key=True)

    created_at: datetime.datetime = sqlmodel.Field(
        sa_column=sqlalchemy.Column(
            sqlalchemy.DateTime(timezone=True),
            nullable=False,
        ),
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
    )
    resource_id: int = sqlmodel.Field(index=True) # e.g 0(all),1,2
    resource_name: str = sqlmodel.Field(index=True, max_length=50) # e.g products, users
    roles: str = sqlmodel.Field(index=True, max_length=10) # e.g m(anage),r(ead),w(rite)
    updated_at: datetime.datetime = sqlmodel.Field(
        sa_column=sqlalchemy.Column(
            sqlalchemy.DateTime(timezone=True),
            nullable=False,
            onupdate=sqlalchemy.sql.func.now(),
        ),
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
    )
    user_id: int = sqlmodel.Field(index=True)
