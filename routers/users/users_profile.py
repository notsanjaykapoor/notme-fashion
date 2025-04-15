import fastapi
import fastapi.responses
import fastapi.templating
import sqlmodel

import context
import log
import main_shared
import services.users

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers", context_processors=[main_shared.jinja_context])

app = fastapi.APIRouter(
    tags=["app"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)


@app.get("/users/{uid}/profile", response_class=fastapi.responses.HTMLResponse)
def users_profile(
    request: fastapi.Request,
    uid: int,
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

    try:
        logger.info(f"{context.rid_get()} user {uid} profile try")

    except Exception as e:
        logger.error(f"{context.rid_get()} user {uid} profile exception '{e}'")

    try:
        response = templates.TemplateResponse(
            request,
            "users/profile.html",
            {
                "app_name": "User Profile",
                "user": user,
                "user_profile": user_profile,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} user {uid} profile render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    return response
