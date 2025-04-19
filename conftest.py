import os

import pytest
import sqlalchemy
import sqlalchemy.future
import sqlmodel
import sqlmodel.pool

import dot_init  # noqa: F401
import models
import services.database
import services.users

# set env vars
os.environ["APP_ENV"] = "tst"
os.environ["SECRETS_BUCKET_URI"] = "gs://notme-secrets-tst"
os.environ["SECRETS_FS_URI"] = "file://localhost//Users/sanjaykapoor/notme/notme-secrets/test/data/bucket-cache/"

test_db_name = os.environ.get("DATABASE_TEST_URL")
connect_args: dict = {}

assert test_db_name

if "sqlite" in test_db_name:
    # sqlite specific
    connect_args = {"check_same_thread": False}

engine = sqlmodel.create_engine(
    test_db_name,
    connect_args=connect_args,
    poolclass=sqlmodel.pool.StaticPool,
)


def database_tables_create(engine: sqlalchemy.future.Engine):
    sqlmodel.SQLModel.metadata.create_all(engine)


def database_tables_drop(engine: sqlalchemy.future.Engine):
    sqlmodel.SQLModel.metadata.drop_all(engine)


# Set up the database once
database_tables_drop(engine)
database_tables_create(engine)


@pytest.fixture(name="db_session")
def session_fixture():
    connection = engine.connect()
    transaction = connection.begin()

    # begin a nested transaction (using SAVEPOINT)
    nested = connection.begin_nested()

    session = sqlmodel.Session(engine)

    # if the application code calls session.commit, it will end the nested transaction
    # when that happens, start a new one.
    @sqlalchemy.event.listens_for(session, "after_transaction_end")
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    # yield session to test
    yield session

    session.close()

    # rollback the overall transaction, restoring the state before the test ran
    transaction.rollback()
    connection.close()


@pytest.fixture(name="user_1")
def user_1_fixture(db_session: sqlmodel.Session):
    user = models.User(
        email="user-1@gmail.com",
        handle="user-1",
        idp=models.user.IDP_GOOGLE,
        state=models.user.STATE_ACTIVE,
    )

    db_session.add(user)
    db_session.commit()

    assert user.id

    yield user

    services.database.truncate_tables(db_session=db_session, table_names=["users"])


@pytest.fixture(name="user_acl_1")
def user_acl_1_fixture(db_session: sqlmodel.Session, user_1: models.User):
    user_acl = models.UserAcl(
        resource_name=models.user_acl.RESOURCE_USERS,
        resource_id=user_1.id,
        roles=models.user_acl.ROLES_ALL,
        user_id=user_1.id
    )

    db_session.add(user_acl)
    db_session.commit()

    assert user_acl.id

    yield user_acl

    services.database.truncate_tables(db_session=db_session, table_names=["user_acls"])


@pytest.fixture(name="bm_1")
def bookmark_1_fixture(db_session: sqlmodel.Session, user_1: models.User):
    bm = models.Bookmark(
        categories=["category-1"],
        name="bookmark-1",
        tags=["tag-1"],
        user_id=user_1.id,
        uri="https://www.google.com",
    )

    db_session.add(bm)
    db_session.commit()

    assert bm.id

    yield bm

    services.database.truncate_tables(db_session=db_session, table_names=["bookmarks"])
    services.database.truncate_tables(db_session=db_session, table_names=["users"])
