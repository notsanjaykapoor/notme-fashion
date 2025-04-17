import os

import dot_init # noqa: F401

import fastapi
import fastapi.templating
import pydantic
import requests

import context
import log
import main_shared

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers", context_processors=[main_shared.jinja_context])

app = fastapi.APIRouter(
    tags=["app"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)

TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

class TurnstileStruct(pydantic.BaseModel):
    token: str

#
# turnstile docs: https://developers.cloudflare.com/turnstile/
# turnstile testing: https://developers.cloudflare.com/turnstile/troubleshooting/testing/
#

@app.get("/turnstile")
def turnstile(request: fastapi.Request):
    logger.info(f"{context.rid_get()} turnstile enter")

    turnstile_site_key = os.environ.get("TURNSTILE_SITE_KEY")

    response = templates.TemplateResponse(
        request,
        "turnstile/turnstile.html",
        {
            "turnstile_site_key": turnstile_site_key,
        },
    )

    return response


@app.post("/turnstile/verify")
def turnstile_verify(request: fastapi.Request, turnstile_struct: TurnstileStruct) -> fastapi.responses.JSONResponse:
    logger.info(f"{context.rid_get()} turnstile verify try")

    data = {
        "secret": os.environ.get("TURNSTILE_SECRET_KEY"),
        "response": turnstile_struct.token,
    }

    turnstile_response = requests.post(TURNSTILE_VERIFY_URL, data=data)

    if turnstile_response.status_code != 200:
        logger.error(f"{context.rid_get()} turnstile error")
        return fastapi.responses.JSONResponse(content={"code": response.status_code}, status_code=200)

    site_response = turnstile_response.json()

    cookie_name = "challenge_ts"

    if not site_response.get("success", False):
        logger.error(f"{context.rid_get()} turnstile error")
        response = fastapi.responses.JSONResponse(content={"code": 400}, status_code=200)
        response.delete_cookie(cookie_name)
    else:
        logger.info(f"{context.rid_get()} turnstile verify ok")

        response = fastapi.responses.JSONResponse(
            content={
                "code": 200,
                "goto": "/gallery",
            },
            status_code=200,
        )

        # set challenge cookie so we don't do this again
        response.set_cookie(key=cookie_name, value=site_response.get("challenge_ts"))

    return response