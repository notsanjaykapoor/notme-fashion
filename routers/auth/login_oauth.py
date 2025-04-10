import datetime
import os
import re
import traceback

import fastapi
import fastapi.responses
import fastapi.templating
import google_auth_oauthlib.flow
import requests
import sqlmodel

import context
import log
import main_shared
import services.users
import services.utils

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers", context_processors=[main_shared.jinja_context])

app = fastapi.APIRouter(
    tags=["app.oauth"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)

oauth_scopes = [
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]


@app.get("/login/denied")
def oauth_login_denied(request: fastapi.Request):
    logger.info(f"{context.rid_get()} oauth login denied")

    return templates.TemplateResponse(
        request,
        "auth/login_denied.html",
        {
            "app_name": "Console",
            "login_message": "Authorization denied",
        },
    )


@app.get("/login/oauth")
def oauth_login():
    """
    docs: https://developers.google.com/identity/protocols/oauth2/web-server
    """
    logger.info(f"{context.rid_get()} oauth init")

    try:
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            services.utils.base64_to_json(s=os.environ.get("OAUTH_SECRETS_BASE64")),
            scopes=oauth_scopes,
        )

        flow.redirect_uri = os.environ.get("OAUTH_REDIRECT_URI")

        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent select_account",
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} oauth exception '{e}'")

    logger.info(f"{context.rid_get()} oauth redirect")

    return fastapi.responses.RedirectResponse(authorization_url)


@app.get("/login/oauth2callback")
def oauth_login_oauth2callback(
    request: fastapi.Request,
    response: fastapi.Response,
    code: str,
    scope: str,
    state: str,
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    logger.info(f"{context.rid_get()} oauth callback try")

    try:
        # exchange authorization code for access token

        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            services.utils.base64_to_json(s=os.environ.get("OAUTH_SECRETS_BASE64")),
            scopes=oauth_scopes,
            state=state,
        )

        logger.info(f"{context.rid_get()} oauth callback token fetch")

        # get request url, make sure its https

        token_request_uri = re.sub("^http:", "https:", str(request.url))
        flow.redirect_uri = os.environ.get("OAUTH_REDIRECT_URI")
        flow.fetch_token(authorization_response=token_request_uri)
        credentials = flow.credentials

        # get user email address from google endpoint

        google_response = requests.get(
            f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={credentials.token}"
        )
        google_response_json = google_response.json()

        user_email = google_response_json.get("email")
        _user_name = google_response_json.get("name") or ""

        # get user
        user = services.users.get_by_email(db_session=db_session, email=user_email)

        if not user:
            logger.error(f"{context.rid_get()} oauth callback user '{user_email}' invalid")
            return fastapi.responses.RedirectResponse("/login/denied")

        # create jwt token

        jwt_expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
        # jwt_expires = credentials.expiry  # google tokens last about an hour

        jwt_token = services.users.jwt_token_create(
            user=user,
            oauth_token=credentials.token,
            oauth_expiry=jwt_expires,
            # refresh_token=credentials.refresh_token,
            # token_uri=credentials.token_uri,
            # client_id=credentials.client_id,
            # client_secret=credentials.client_secret,
        )
    except Exception as e:
        jwt_token = ""
        logger.error(f"{context.rid_get()} oauth callback exception '{e}' - {traceback.format_exc()}")
        return fastapi.responses.RedirectResponse("/login/denied")

    logger.info(f"{context.rid_get()} oauth callback ok")

    response = fastapi.responses.RedirectResponse("/")
    response.set_cookie(key="session_id", value=jwt_token)

    return response