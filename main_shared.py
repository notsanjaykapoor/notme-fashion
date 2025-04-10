import os

import fastapi

import context
import services.database.session


# sync db dependency
def get_db():
    with services.database.session.get() as session:
        yield session


# async db dependency (e.g. gql)
async def get_gql_context(db=fastapi.Depends(get_db)):
    return {"db": db}


def get_user_id():
    yield context.uid_get()


def jinja_context(request: fastapi.Request) -> dict[str]:
    return {
        "app_version": os.environ.get("APP_VERSION", ""),
        "user_id": context.uid_get(),
        "vps_key": os.environ.get("VPS_KEY", ""),
    }
