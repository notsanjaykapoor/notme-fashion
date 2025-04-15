import os

import dot_init # noqa: F401

import contextlib
import fastapi
import fastapi.middleware.cors
import fastapi.staticfiles
import fastapi.templating
import sqlmodel
import starlette.middleware.sessions
import ulid

import context
import log
import main_shared
import routers.auth.login
import routers.auth.login_oauth
import routers.auth.logout
import routers.gallery.gallery
import routers.products.products_list
import routers.products.products_manage
import routers.products.products_show
import routers.site.site
import routers.users.users_profile
import routers.users.users_link
import services.database
import services.users

logger = log.init("app")

@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    logger.info("api.startup init")

    if services.database.session.check() != 0:
        # create database
        services.database.session.create()

    # migrate database
    services.database.session.migrate()

    logger.info("api.startup completed")

    yield

    logger.info("api.startup exiting")


# create app object
app = fastapi.FastAPI(lifespan=lifespan)

app.include_router(routers.auth.login.app)
app.include_router(routers.auth.login_oauth.app)
app.include_router(routers.auth.logout.app)
app.include_router(routers.gallery.gallery.app)
app.include_router(routers.products.products_list.app)
app.include_router(routers.products.products_manage.app)
app.include_router(routers.products.products_show.app)
app.include_router(routers.site.site.app)
app.include_router(routers.users.users_profile.app)
app.include_router(routers.users.users_link.app)

# mount traditional static directory
app.mount("/static", fastapi.staticfiles.StaticFiles(directory="static"), name="static")

app.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    starlette.middleware.sessions.SessionMiddleware,
    secret_key=os.environ.get("FASTAPI_SESSION_KEY", ""),
    max_age=None,
)

@app.middleware("http")
async def notme_middleware(request: fastapi.Request, call_next):
    # set request id context var
    context.rid_set(ulid.new().str)

    # set user_id context var
    session_id = request.cookies.get("session_id", "")
    if jwt_user := services.users.jwt_token_decode(token=session_id):
        user_id = jwt_user.get("user_id")
    else:
        user_id=0

    context.uid_set(id=user_id)

    response = await call_next(request)
    return response


# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers", context_processors=[main_shared.jinja_context])


@app.get("/favicon.ico")
def favicon():
    file_name = "favicon.ico"
    file_path = os.path.join(app.root_path, "static", file_name)
    return fastapi.responses.FileResponse(
        path=file_path,
        headers={"Content-Disposition": "attachment; filename=" + file_name},
    )


@app.get("/")
def home():
    logger.info(f"{context.rid_get()} home")

    return fastapi.responses.RedirectResponse("/gallery")


@app.get("/500")
def error_500(request: fastapi.Request):
    return templates.TemplateResponse(
        request,
        "500.html",
        {
            "app_name": "Error",
        }
    )
