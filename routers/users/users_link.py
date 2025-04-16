import fastapi
import fastapi.responses
import fastapi.templating
import sqlalchemy.orm.attributes
import sqlmodel
import ulid

import context
import log
import main_shared
import models
import services.grailed
import services.ig
import services.users

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers", context_processors=[main_shared.jinja_context])

app = fastapi.APIRouter(
    tags=["app"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)


@app.get("/users/{uid}/link/{link_name}", response_class=fastapi.responses.HTMLResponse)
def users_link(
    request: fastapi.Request,
    uid: int,
    link_name: str,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    """
    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    if user_id != uid:
        # temporary
        return fastapi.responses.RedirectResponse("/gallery")

    user_profile = services.users.get_by_id(db_session=db_session, id=uid)

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    logger.info(f"{context.rid_get()} user {user_profile.id} link '{link_name}' try")

    try:
        if link_name == "grailed":
            key_name = "grailed_key"
            key_value = user_profile.grailed_key
        elif link_name == "instagram":
            key_name = "ig_key"
            key_value = user_profile.ig_key

        if not key_value:
            key_value = ulid.new().str
            user_profile.data = user_profile.data | {key_name : key_value}
            sqlalchemy.orm.attributes.flag_modified(user_profile, "data")
            db_session.add(user_profile)
            db_session.commit()

        logger.info(f"{context.rid_get()} user {user_profile.id} link '{link_name}' ok")
    except Exception as e:
        logger.error(f"{context.rid_get()} user {user_profile.id} link '{link_name}' exception '{e}'")

    if link_name == "grailed":
        key_prompt = "https://www.grailed.com/listings/123456789"
    elif link_name == "instagram":
        key_prompt = "https://www.instagram.com/p/xYZe6z4qlqD/"

    template_name = f"users/link_{link_name}.html"

    try:
        response = templates.TemplateResponse(
            request,
            template_name,
            {
                "app_name": f"Link {link_name.title()}",
                "key_value": key_value,
                "key_prompt": key_prompt,
                "link_name": link_name,
                "user": user,
                "user_profile": user_profile,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} user {uid} profile render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    return response


@app.get("/users/{uid}/verify/{link_name}", response_class=fastapi.responses.PlainTextResponse | fastapi.responses.RedirectResponse)
def users_verify(
    request: fastapi.Request,
    uid: int,
    link_name: str,
    url: str,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    """
    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    if user_id != uid:
        # temporary
        return fastapi.responses.RedirectResponse("/gallery")

    user_profile = services.users.get_by_id(db_session=db_session, id=uid)

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    logger.info(f"{context.rid_get()} user {user_profile.id} verify '{link_name}' try")

    try:
        if link_name == "grailed":
            key_value = user_profile.grailed_key
        elif link_name == "instagram":
            key_value = user_profile.ig_key

        if not key_value:
            raise ValueError(f"{link_name} key not found")

        if link_name == "grailed":
            verify_result = services.grailed.verify(url=url, key=key_value)

            print(verify_result) # xxx

            if verify_result.code != 0:
                raise Exception(", ".join(verify_result.errors))

            # update user grailed handle
            user_profile.grailed_handle = verify_result.listing.username
        elif link_name == "instagram":
            verify_result = services.ig.verify(url=url, key=key_value)

            if verify_result.code != 0:
                raise Exception(", ".join(verify_result.errors))

            # update user ig handle
            user_profile.ig_handle = verify_result.post.username

        if user_profile.state != models.user.STATE_VERIFIED:
            user_profile.state = models.user.STATE_VERIFIED

        db_session.add(user_profile)
        db_session.commit(user_profile)

        verify_code = 0
        verify_message = ""
        logger.info(f"{context.rid_get()} user {user_profile.id} verify '{link_name}' ok")
    except Exception as e:
        verify_code = 400
        verify_message = str(e)
        logger.error(f"{context.rid_get()} user {user_profile.id} verify '{link_name}' exception '{e}'")

    response = fastapi.responses.PlainTextResponse(verify_message)

    if verify_code == 0:
        # htmx redirect
        response.headers["HX-Redirect"] = f"/users/{user_profile.id}/profile"

    return response
