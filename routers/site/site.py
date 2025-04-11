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

@app.get("/site/about", response_class=fastapi.responses.HTMLResponse)
def site_about(
    request: fastapi.Request,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    """
    logger.info(f"{context.rid_get()} site about")

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    response = templates.TemplateResponse(
        request,
        "site/about.html",
        {
            "app_name": "About",
            "user": user,
        }
    )

    return response
