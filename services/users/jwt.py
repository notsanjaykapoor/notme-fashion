import datetime
import os
import re

import jwt

import models

JWT_ALGORITHM = "HS256"


def jwt_token_create(user: models.User, oauth_token: str, oauth_expiry: datetime.datetime) -> str:
    jwt_payload = {
        "exp": oauth_expiry,
        "sub": os.environ["JWT_ISSUER"],
        "oauth_token": oauth_token,
        "user_id": user.id,
        "user_email": user.email,
        "user_tz": models.user.TZ_DEFAULT,  # default value
    }

    return jwt.encode(jwt_payload, os.environ["JWT_SECRET"], algorithm=JWT_ALGORITHM)


def jwt_token_decode(token: str) -> dict:
    try:
        token_raw = re.sub("(Bearer|bearer)\s+", "", token)
        return jwt.decode(
            token_raw, os.environ["JWT_SECRET"], algorithms=[JWT_ALGORITHM]
        )
    except Exception:
        return {}