import sqlmodel

import models
import services.users.acls


def manage_product(db_session: sqlmodel.Session, user: models.User, resource: models.Product) -> int:
    """
    Returns 1 if  user is allowed to manage the product resource.

    The check is done with the following queries:
      - user has manage role on product.user.id
      - user has manage role on product.id or all products
    """
    role = models.user_acl.ROLES_MANAGE

    queries = [
        f"name:{models.user_acl.RESOURCE_USERS} id:{resource.user_id} user:{user.id} role:{role}",
        f"name:{models.user_acl.RESOURCE_PRODUCTS} ids:0,{resource.id} user:{user.id} role:{role}",
    ]

    for query in queries:
        list_struct = services.users.acls.list(
            db_session=db_session,
            query=query,
            offset=0,
            limit=1,
        )

        if list_struct.total > 0:
            return list_struct.total

    return 0


def manage_products(db_session: sqlmodel.Session, user: models.User) -> int:
    """
    Returns 1 if user is allowed to manage all products.
    """
    key = models.user_acl.RESOURCE_PRODUCTS
    role = models.user_acl.ROLES_MANAGE

    list_struct = services.users.acls.list(
        db_session=db_session,
        query=f"name:{key} id:0 user:{user.id} role:{role}",
        offset=0,
        limit=1,
    )

    return list_struct.total


def manage_user(db_session: sqlmodel.Session, user: models.User, resource: models.User) -> int:
    """
    Returns 1 if user is allowed to manage the user resource.
    """
    key = models.user_acl.RESOURCE_USERS
    role = models.user_acl.ROLES_MANAGE

    list_struct = services.users.acls.list(
        db_session=db_session,
        query=f"name:{key} id:0,{resource.id} user:{user.id} role:{role}",
        offset=0,
        limit=1,
    )

    return list_struct.total


def manage_users(db_session: sqlmodel.Session, user: models.User) -> int:
    """
    Returns 1 if user is allowed to manage all users.
    """
    key = models.user_acl.RESOURCE_USERS
    role = models.user_acl.ROLES_MANAGE

    list_struct = services.users.acls.list(
        db_session=db_session,
        query=f"name:{key} id:0 user:{user.id} role:{role}",
        offset=0,
        limit=1,
    )

    return list_struct.total
