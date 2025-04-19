import sqlmodel

import models
import services.users.acls


def create_default(db_session: sqlmodel.Session, user: models.User) -> tuple[int, models.User | None]:
    """
    Create default user acl, which gives users manage, read, write roles over all their resources.
    """
    name = models.user_acl.RESOURCE_USERS
    rid = user.id

    list_struct = services.users.acls.list(
        db_session=db_session,
        query=f"name:{name} id:{rid} role:{models.user_acl.ROLES_MANAGE} user:{user.id}",
        offset=0,
        limit=1,
    )

    if list_struct.objects:
        return 409, list_struct.objects[0]
    
    user_acl = models.UserAcl(
        roles=models.user_acl.ROLES_ALL,
        resource_name=name,
        resource_id=rid,
        user_id=user.id,
    )

    db_session.add(user_acl)
    db_session.commit()

    return 0, user_acl


def create_superuser(db_session: sqlmodel.Session, user: models.User) -> tuple[int, models.User | None]:
    """
    Create superuser user acl, which gives users manage, read, write roles over all resources.
    """
    name = models.user_acl.RESOURCE_USERS
    rid = 0

    list_struct = services.users.acls.list(
        db_session=db_session,
        query=f"name:{name} id:{rid} role:{models.user_acl.ROLES_MANAGE} user:{user.id}",
        offset=0,
        limit=1,
    )

    if list_struct.objects:
        return 409, list_struct.objects[0]
    
    user_acl = models.UserAcl(
        roles=models.user_acl.ROLES_ALL,
        resource_name=name,
        resource_id=rid,
        user_id=user.id,
    )

    db_session.add(user_acl)
    db_session.commit()

    return 0, user_acl

