import sqlmodel

import models
import services.database
import services.users.acls


def test_users_acls_create_default(db_session: sqlmodel.Session, user_1: models.User):
    # should create default acl

    code, user_acl = services.users.acls.create_default(
        db_session=db_session,
        user=user_1,
    )    

    assert code == 0
    assert user_acl.id
    assert user_acl.roles == "mrw"
    assert user_acl.resource_name == "users"
    assert user_acl.resource_id == user_1.id
    assert user_acl.user_id == user_1.id

   # should be idempotent

    code, user_acl_ = services.users.acls.create_default(
        db_session=db_session,
        user=user_1,
    )    

    assert code == 409
    assert user_acl_.id == user_acl.id
 
    # should be able to manage user

    code = services.users.acls.manage_user(
        db_session=db_session,
        user=user_1,
        resource=user_1,
    )

    assert code == 1

    # should not be able to manage all users

    code = services.users.acls.manage_users(
        db_session=db_session,
        user=user_1,
    )

    assert code == 0

    services.database.truncate_tables(db_session=db_session, table_names=["user_acls"])


def test_users_acls_create_superuser(db_session: sqlmodel.Session, user_1: models.User):
    # should create superuser acl

    code, user_acl = services.users.acls.create_superuser(
        db_session=db_session,
        user=user_1,
    )    

    assert code == 0
    assert user_acl.id
    assert user_acl.roles == "mrw"
    assert user_acl.resource_name == "users"
    assert user_acl.resource_id == 0
    assert user_acl.user_id == user_1.id

    # should be able to manage any user

    code = services.users.acls.manage_user(
        db_session=db_session,
        user=user_1,
        resource=user_1,
    )

    assert code == 1

    code = services.users.acls.manage_users(
        db_session=db_session,
        user=user_1,
    )

    assert code == 1
