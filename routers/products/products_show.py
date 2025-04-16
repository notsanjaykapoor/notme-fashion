import fastapi
import fastapi.templating
import sqlmodel
import urllib.parse

import context
import log
import main_shared
import services.products
import services.products.images
import services.users

logger = log.init("app")

# initialize templates dir
templates = fastapi.templating.Jinja2Templates(directory="routers", context_processors=[main_shared.jinja_context])
templates.env.filters["quote_plus"] = lambda s: urllib.parse.quote_plus(str(s)) if s else ""

app = fastapi.APIRouter(
    tags=["app"],
    dependencies=[fastapi.Depends(main_shared.get_db)],
    responses={404: {"description": "Not found"}},
)

@app.get("/products/{product_id}", response_class=fastapi.responses.HTMLResponse)
def products_show(
    request: fastapi.Request,
    product_id: int,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    user = services.users.get_by_id(db_session=db_session, id=user_id)

    logger.info(f"{context.rid_get()} product {product_id} try")

    if "edit" in (referer_path := request.headers.get("referer", "")):
        referer_path = "/gallery"

    try:
        product = services.products.get_by_id(
            db_session=db_session,
            id=product_id,
        )

        list_result = services.products.images.list(
            db_session=db_session,
            query=f"product_id:{product.id}",
            sort="id+",
        )
        images_list = list_result.objects
        images_count = len(images_list)

        for image in images_list:
            # transform uri
            image.url = services.products.images.transform(product=product, image=image, transform="tr:w-400")

        logger.info(f"{context.rid_get()} product {product_id} ok")
    except Exception as e:
        logger.error(f"{context.rid_get()} product {product_id} exception '{e}'")
        return fastapi.responses.RedirectResponse(referer_path)

    if images_count == 1:
        masonry_columns = "columns-1"
        masonry_width = "w-4/12"
    elif images_count == 2:
        masonry_columns = "columns-2"
        masonry_width = "w-8/12"
    else:
        masonry_columns = "columns-3"
        masonry_width = "w-10/12"

    if "HX-Request" in request.headers:
        template = "products/show_table.html"
    else:
        template = "products/show.html"

    try:
        response = templates.TemplateResponse(
            request,
            template,
            {
                "app_name": "Product Details",
                "images_count": images_count,
                "images_list": images_list,
                "masonry_columns": masonry_columns,
                "masonry_width": masonry_width,
                "product": product,
                "referer_path": referer_path,
                "user": user,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} product {product_id} render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    return response
