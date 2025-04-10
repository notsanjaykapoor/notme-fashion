import fastapi
import fastapi.responses

import context
import log
import main_shared

logger = log.init("app")

app = fastapi.APIRouter(
    tags=["app.oauth"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)


@app.get("/logout")
def logout():
    """ """
    logger.info(f"{context.rid_get()} logout")

    response = fastapi.responses.RedirectResponse("/")
    response.delete_cookie("session_id")

    return response