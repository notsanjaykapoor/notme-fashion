import random

import sqlmodel

import models
import services.users.acls


def test_users_acls_manage_products(db_session: sqlmodel.Session, user_1: models.User, user_acl_1: models.UserAcl):
    code = services.users.acls.manage_products(
        db_session=db_session,
        user=user_1,
    )

    assert code == 0

    product_1 = models.Product(
        id=random.randint(1, 1000),
        name="product-1",
        user_id=user_1.id,
    )

    code = services.users.acls.manage_product(
        db_session=db_session,
        resource=product_1,
        user=user_1,
    )

    assert code == 1


def test_users_acls_roles_expand():
    assert services.users.acls.roles_expand(roles=models.user_acl.ROLES_ALL) == "mrw"

    assert services.users.acls.roles_expand(roles="r") == "r"
    assert services.users.acls.roles_expand(roles="w") == "rw"
    assert services.users.acls.roles_expand(roles="m") == "mrw"
    assert services.users.acls.roles_expand(roles="mr") == "mrw"
    assert services.users.acls.roles_expand(roles="mw") == "mrw"
