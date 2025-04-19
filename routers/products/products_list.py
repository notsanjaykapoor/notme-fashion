import fastapi
import fastapi.responses
import fastapi.templating
import sqlmodel

import context
import log
import main_shared
import routers.utils
import services.products
import services.users
import services.users.acls

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers", context_processors=[main_shared.jinja_context])

app = fastapi.APIRouter(
    tags=["app"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)


@app.get("/products", response_class=fastapi.responses.HTMLResponse)
def products_list(
    request: fastapi.Request,
    query: str="",
    offset: int=0,
    limit: int=20,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    if services.users.acls.manage_users(db_session=db_session, user=user) != 1:
        logger.error(f"{context.rid_get()} products query '{query}' not authorized")
        return fastapi.responses.RedirectResponse("/gallery")

    logger.info(f"{context.rid_get()} products query '{query}' try")

    try:
        list_result = services.products.list(
            db_session=db_session,
            query=query,
            offset=offset,
            limit=limit,
            sort="id-",
            scope="",
        )
        products_list = list_result.objects
        products_count = len(products_list)
        total_count = list_result.total
        time_msec = list_result.msec

        query_code = 0

        if total_count <= limit:
            query_result = f"query '{query}' returned {total_count} results in {time_msec} msec"
        else:
            query_result = f"query '{query}' returned {offset+1} - {offset+products_count} of {total_count} results in {time_msec} msec"

        logger.info(f"{context.rid_get()} products query '{query}' ok")
    except Exception as e:
        products_list = []

        query_code = 500
        query_result = f"exception {e}"

        logger.error(f"{context.rid_get()} products query '{query}' exception '{e}'")

    page_prev, page_next = routers.utils.page_links(
        path=request.url.path,
        params=request.query_params,
        limit=limit,
        total=total_count
    )

    if "HX-Request" in request.headers:
        template = "products/list_table.html"
    else:
        template = "products/list.html"

    try:
        response = templates.TemplateResponse(
            request,
            template,
            {
                "app_name": "Products",
                "page_next": page_next,
                "page_prev": page_prev,
                "products_list": products_list,
                "query": query,
                "query_code": query_code,
                "query_result": query_result,
                "user": user,
            }
        )

        if "HX-Request" in request.headers:
            response.headers["HX-Push-Url"] = f"/products?query={query}"
    except Exception as e:
        logger.error(f"{context.rid_get()} products query '{query}' render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    return response
