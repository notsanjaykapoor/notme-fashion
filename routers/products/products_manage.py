import fastapi
import fastapi.responses
import fastapi.templating
import re
import sqlalchemy.orm.attributes
import sqlmodel
import ulid

import context
import log
import main_shared
import models
import services.grailed
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

@app.get("/products/create", response_class=fastapi.responses.HTMLResponse)
def products_create(
    request: fastapi.Request,
    name: str,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    """
    """
    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    user = services.users.get_by_id(db_session=db_session, id=user_id)
    name = name.strip().lower()

    logger.info(f"{context.rid_get()} product create '{name}' try")

    try:
        if name.startswith("grailed:"):
            _, grailed_id = name.split(":")

            # check if product exists

            product = services.products.get_by_grailed_id(
                db_session=db_session,
                grailed_id=grailed_id,
            )

            if product:
                raise Exception(f"product {product.id} exists")

            # download and parse grailed listing

            code, html_path = services.grailed.download(grailed_id=grailed_id)

            if code not in [0, 409]:
                raise Exception(f"download error {code}")

            parse_result = services.grailed.parse(html_path=html_path)

            if parse_result.code != 0:
                raise Exception(f"parse error {parse_result.code}")

            name = parse_result.name
            image_urls = parse_result.image_urls[0:2]
        else:
            image_urls = []
            grailed_id = 0

        product = services.products.create(
            db_session=db_session,
            grailed_id=grailed_id,
            key=ulid.new().str,
            name=name,
            source_id=ulid.new().str,
            source_name=models.product.SOURCE_NOTME,
            state=models.product.STATE_DRAFT,
            user_id=user.id,
        )

        for image_url in image_urls:
            image_url = re.sub(r"\?.*", "", image_url)

            code, _image = services.products.images.create(
                db_session=db_session,
                product=product,
                folder="/products",
                url=image_url,
            )

        services.products.sync_images(
            db_session=db_session,
            product=product,
        )

        redirect_path = f"/products/{product.id}/edit"
        logger.info(f"{context.rid_get()} product create '{name}' ok - product {product.id}")
    except Exception as e:
        redirect_path = f"/products"
        logger.error(f"{context.rid_get()} product create exception '{e}'")

    if "HX-Request" in request.headers:
        response = templates.TemplateResponse(request, "201.html")
        response.headers["HX-Redirect"] = redirect_path
        return response
    else:
        return fastapi.responses.RedirectResponse(redirect_path)


@app.get("/products/{product_id}/add", response_class=fastapi.responses.HTMLResponse)
def products_image_add(
    request: fastapi.Request,
    product_id: int,
    image_url: str,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    logger.info(f"{context.rid_get()} product {product_id} image '{image_url}' add try")

    try:
        product = services.products.get_by_id(
            db_session=db_session,
            id=product_id,
        )

        # add image
        code, _image = services.products.images.create(
            db_session=db_session,
            product=product,
            folder="/products",
            url=image_url,
        )

        if code != 0:
            raise Exception(f"image create error {code}")

        # sync image metadata
        services.products.sync_images(
            db_session=db_session,
            product=product,
        )

        list_result = services.products.images.list(
            db_session=db_session,
            query=f"product_id:{product.id}",
        )
        images_list = list_result.objects
        images_count = len(images_list)

        thumbnails_map = {
            image.id : services.products.images.transform(product=product, image=image, transform="tr:w-30") for image in images_list
        }

        logger.info(f"{context.rid_get()} product {product_id} image '{image_url}' add ok")
    except Exception as e:
        logger.error(f"{context.rid_get()} product {product_id} image add exception '{e}'")
        

    if "HX-Request" in request.headers:
        template = "products/edit_images.html"
    else:
        template = ""

    try:
        response = templates.TemplateResponse(
            request,
            template,
            {
                "app_name": "Product Edit",
                "images_count": images_count,
                "images_list": images_list,
                "product": product,
                "thumbnails_map": thumbnails_map,
                "user": user,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} product {product_id} edit render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    return response


@app.get("/products/{product_id}/delete", response_class=fastapi.responses.HTMLResponse)
def products_image_delete(
    request: fastapi.Request,
    product_id: int,
    image_id: int,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    logger.info(f"{context.rid_get()} product {product_id} image {image_id} delete try")

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
        image = [image for image in images_list if image.id == image_id][0]

        # delete image from imagekit and database
        services.products.images.delete(
            db_session=db_session,
            product=product,
            image=image,
        )

        # sync image metadata
        services.products.sync_images(
            db_session=db_session,
            product=product,
        )

        logger.info(f"{context.rid_get()} product {product_id} image {image_id} delete ok")
    except Exception as e:
        logger.error(f"{context.rid_get()} product {product_id} image {image_id} delete exception '{e}'")

    return fastapi.responses.RedirectResponse(request.headers.get("referer"))


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

    referer_path = request.headers.get("referer", "")

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
        images_count = len(images_list)

        thumbnails_map = {
            image.id : services.products.images.transform(product=product, image=image, transform="tr:w-30") for image in images_list
        }

        logger.info(f"{context.rid_get()} product {product_id} edit ok")
    except Exception as e:
        logger.error(f"{context.rid_get()} product {product_id} edit exception '{e}'")
        return fastapi.responses.RedirectResponse(referer_path)

    if "HX-Request" in request.headers:
        template = ""
    else:
        template = "products/edit.html"

    try:
        response = templates.TemplateResponse(
            request,
            template,
            {
                "app_name": "Product Edit",
                "images_count": images_count,
                "images_list": images_list,
                "product": product,
                "referer_path": referer_path,
                "thumbnails_map": thumbnails_map,
                "user": user,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} product {product_id} edit render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    return response


@app.get("/products/{product_id}/publish", response_class=fastapi.responses.HTMLResponse)
def products_publish(
    request: fastapi.Request,
    product_id: int,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    logger.info(f"{context.rid_get()} product {product_id} publish try")

    try:
        product = services.products.get_by_id(
            db_session=db_session,
            id=product_id,
        )

        if product.state == models.product.STATE_DRAFT:
            product.state = models.product.STATE_ACTIVE
            db_session.add(product)
            db_session.commit()

        logger.info(f"{context.rid_get()} product {product_id} publish ok")
    except Exception as e:
        logger.error(f"{context.rid_get()} product {product_id} publish exception '{e}'")

    redirect_path = f"/products/{product.id}/edit"

    if "HX-Request" in request.headers:
        response = templates.TemplateResponse(request, "201.html")
        response.headers["HX-Redirect"] = redirect_path
        return response
    else:
        return fastapi.responses.RedirectResponse(redirect_path)


@app.get("/products/{product_id}/update", response_class=fastapi.responses.HTMLResponse)
def products_update(
    request: fastapi.Request,
    product_id: int,
    brands: str = "",
    grailed_id: int = 0,
    name: str = "",
    color: str = "",
    material: str = "",
    model: str = "",
    season: str = "",
    size: str = "",
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    logger.info(f"{context.rid_get()} product {product_id} update try")

    try:
        product = services.products.get_by_id(
            db_session=db_session,
            id=product_id,
        )

        if brands:
            brands_list = [s.strip().lower() for s in brands.split(",") if s]
            product.brands = brands_list

        if grailed_id:
            product.grailed_id = grailed_id

        if name:
            product.name = name

        # data attributes

        data_mod = product.data

        if color:
            data_mod["color"] = color.lower()
            product.data = data_mod
            sqlalchemy.orm.attributes.flag_modified(product, "data")

        if material:
            data_mod["material"] = material.lower()
            product.data = data_mod
            sqlalchemy.orm.attributes.flag_modified(product, "data")

        if model:
            data_mod["model"] = model.lower()
            product.data = data_mod
            sqlalchemy.orm.attributes.flag_modified(product, "data")

        if season:
            data_mod["season"] = season.lower()
            product.data = data_mod
            sqlalchemy.orm.attributes.flag_modified(product, "data")

        if size:
            data_mod["size"] = size.lower()
            product.data = data_mod
            sqlalchemy.orm.attributes.flag_modified(product, "data")

        db_session.add(product)
        db_session.commit()

        status_message = "changes saved"

        logger.info(f"{context.rid_get()} product {product_id} update ok")
    except Exception as e:
        status_message = str(e)
        logger.error(f"{context.rid_get()} product {product_id} update exception '{e}'")

    if "HX-Request" in request.headers:
        template = "products/edit_data.html"
    else:
        template = ""

    try:
        response = templates.TemplateResponse(
            request,
            template,
            {
                "product": product,
                "status_message": status_message,
                "user": user,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} product {product_id} update render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    return response
