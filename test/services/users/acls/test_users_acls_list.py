import sqlmodel

import models
import services.database
import services.users.acls


def test_users_acls_list(db_session: sqlmodel.Session, user_1: models.User):
    # create acl with rw role on a single user

    acl_1 = models.UserAcl(
        roles="rw",
        resource_name="users",
        resource_id=user_1.id,
        user_id=user_1.id,
    )

    # create acl with m role on all users

    acl_2 = models.UserAcl(
        roles="mrw",
        resource_name="users",
        resource_id=0,
        user_id=user_1.id,
    )

    db_session.add(acl_1)
    db_session.add(acl_2)
    db_session.commit()

    assert acl_1.id
    assert acl_1.roles == "rw"

    # should find acl with valid key,val

    acl_struct = services.users.acls.list(
        db_session=db_session,
        query=f"name:users id:{user_1.id} user:{user_1.id}",
        offset=0,
        limit=10,
    )

    assert acl_struct.code == 0
    assert acl_struct.total == 1
    assert acl_struct.objects[0] == acl_1

    # should find acl with valid key,val,role

    acl_struct = services.users.acls.list(
        db_session=db_session,
        query=f"name:users id:{user_1.id} role:r user:{user_1.id}",
        offset=0,
        limit=10,
    )

    assert acl_struct.code == 0
    assert acl_struct.total == 1
    assert acl_struct.objects[0] == acl_1

    # should find superuser acl with valid key,val,role

    acl_struct = services.users.acls.list(
        db_session=db_session,
        query=f"name:users id:0 role:m user:{user_1.id}",
        offset=0,
        limit=10,
    )

    assert acl_struct.code == 0
    assert acl_struct.total == 1
    assert acl_struct.objects[0] == acl_2

    # should find no acl with invalid role

    acl_struct = services.users.acls.list(
        db_session=db_session,
        query=f"name:users id:{user_1.id} role:m user:{user_1.id}",
        offset=0,
        limit=10,
    )

    assert acl_struct.code == 0
    assert acl_struct.total == 0
    assert acl_struct.objects == []

    services.database.truncate_tables(db_session=db_session, table_names=["user_acls"])
