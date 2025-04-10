import fastapi
import fastapi.responses
import fastapi.templating
import sqlmodel

import context
import log
import main_shared
import services.products
import services.users

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers", context_processors=[main_shared.jinja_context])

app = fastapi.APIRouter(
    tags=["app"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)


@app.get("/products/{product_id}/edit", response_class=fastapi.responses.HTMLResponse)
def products_edit(
    request: fastapi.Request,
    product_id: int,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    logger.info(f"{context.rid_get()} product {product_id} edit try")

    referer_path = request.headers.get("referer")

    try:
        product = services.products.get_by_id(
            db_session=db_session,
            id=product_id,
        )

        list_result = services.products.images.list(
            db_session=db_session,
            query=f"product_id:{product.id}",
        )
        images_list = list_result.objects

        logger.info(f"{context.rid_get()} product {product_id} edit ok")
    except Exception as e:
        logger.error(f"{context.rid_get()} product {product_id} edit exception '{e}'")
        return fastapi.responses.RedirectResponse(referer_path)

    if "HX-Request" in request.headers:
        template = "products/edit_table.html"
    else:
        template = "products/edit.html"

    try:
        response = templates.TemplateResponse(
            request,
            template,
            {
                "app_name": "Product Edit",
                "images_list": images_list,
                "product": product,
                "referer_path": referer_path,
                "user": user,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} product {product_id} edit render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    return response
