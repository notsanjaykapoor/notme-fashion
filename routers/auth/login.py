import datetime
import os

import fastapi
import fastapi.responses
import fastapi.templating
import pydantic
import sqlmodel

import context
import log
import main_shared
import models
import services.users

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers", context_processors=[main_shared.jinja_context])

app = fastapi.APIRouter(
    tags=["app.oauth"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)

class UserPassStruct(pydantic.BaseModel):
    email: str = ""
    password: str = ""


@app.get("/login")
@app.post("/login")
def users_login(
    request: fastapi.Request,
    user_struct: UserPassStruct = None,
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
    user_id: int = fastapi.Depends(main_shared.get_user_id),
):
    """
    user login page
    """
    user_struct = user_struct or UserPassStruct(email="", password="")
    user_email = user_struct.email
    user_pass = user_struct.password

    logger.info(f"{context.rid_get()} users login '{user_email}'")

    if user_id:
        # assume this is always a regular http request
        logger.info(f"{context.rid_get()} users login '{user_email}' redirect")
        return fastapi.responses.RedirectResponse("/")

    if user_email:
        user = services.users.get_by_email(db_session=db_session, email=user_email)

        if not user:
            logger.info(f"{context.rid_get()} users login '{user_email}' email invalid")
            return templates.TemplateResponse(
                request,
                "auth/login_error.html",
                {
                    "email": user_email,
                    "login_message": "invalid email",
                },
            )

        if user.idp == models.user.IDP_GOOGLE:
            response = templates.TemplateResponse(request, "/auth/login_ok.html")
            response.headers["HX-Redirect"] = "/login/oauth"
            return response

    if user_pass:
        login_pass = os.environ.get("OAUTH_PASS", "")

        if not user or not login_pass or user_pass != login_pass:
            logger.info(f"{context.rid_get()} users login '{user_email}' credentials invalid")
            return templates.TemplateResponse(
                request,
                "auth/login_error.html",
                {
                    "email": user_email,
                    "login_error": "invalid credentials",
                },
            )

        jwt_expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)

        jwt_token = services.users.jwt_token_create(
            user=user,
            oauth_token="dev",
            oauth_expiry=jwt_expires,
        )

        logger.info(f"{context.rid_get()} users login '{user_email}' ok")

        response = templates.TemplateResponse(request, "/auth/login_ok.html")
        response.set_cookie(key="session_id", value=jwt_token)
        response.headers["HX-Redirect"] = "/"

        return response

    return templates.TemplateResponse(
        request,
        "auth/login.html",
        {
            "app_name": "Login",
            "email": user_email,
            "prompt_text": "email",
        },
    )