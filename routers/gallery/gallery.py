import fastapi
import fastapi.responses
import fastapi.templating
import sqlmodel

import context
import log
import main_shared
import models
import services.products
import services.products.images
import services.users

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers", context_processors=[main_shared.jinja_context])

app = fastapi.APIRouter(
    tags=["app"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)


@app.get("/gallery", response_class=fastapi.responses.HTMLResponse)
def gallery_list(
    request: fastapi.Request,
    name: str="",
    query: str="",
    offset: int=0,
    limit: int=20,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    user = services.users.get_by_id(db_session=db_session, id=user_id)

    logger.info(f"{context.rid_get()} gallery query '{query}' try")

    try:
        list_result = services.products.list(
            db_session=db_session,
            query=query,
            offset=offset,
            limit=limit,
        )
        products_list = list_result.objects
        total_count = list_result.total

        images_map = {
            product.id : services.products.images.transform(product=product, transform="tr:w-300") for product in products_list
        }

        query_code = 0
        query_result = f"query '{query}' returned {list_result.count} results"

        logger.info(f"{context.rid_get()} gallery query '{query}' ok")
    except Exception as e:
        products_list = []
        images_map = {}

        query_code = 500
        query_result = f"exception {e}"

        logger.error(f"{context.rid_get()} gallery query '{query}' exception '{e}'")

    search_list =[
        models.ProductSearch(name="all", query=""),
        models.ProductSearch(name="for sale", query="state:sell"),
        models.ProductSearch(name="pants", query="category:pants"),
        models.ProductSearch(name="tops", query="category:tops"),
        models.ProductSearch(name="knitwear", query="category:knitwear"),
    ]

    if "HX-Request" in request.headers:
        template = "gallery/list_masonry.html"
    else:
        template = "gallery/list.html"

    if name:
        app_name = f"Gallery - {name.title()}"
    else:
        app_name = "Gallery"

    try:
        response = templates.TemplateResponse(
            request,
            template,
            {
                "app_name": app_name,
                "images_map": images_map,
                "page_limit": limit,
                "page_offset": offset,
                "products_list": products_list,
                "query": query,
                "query_code": query_code,
                "query_result": query_result,
                "search_list": search_list,
                "total_count": total_count,
                "user": user,
            }
        )

        if "HX-Request" in request.headers:
            response.headers["HX-Push-Url"] = f"/gallery?query={query}"
    except Exception as e:
        logger.error(f"{context.rid_get()} gallery query '{query}' render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    return response
