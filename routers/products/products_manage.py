import io
import os
import re

import fastapi
import fastapi.responses
import fastapi.templating
import numpy
import PIL.Image
import rembg
import requests
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

@app.get("/products/create", response_class=fastapi.responses.HTMLResponse | fastapi.responses.PlainTextResponse)
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
        # check if name is a grailed url
        if grailed_url := services.grailed.listing_url_match(url=name):
            # check if user has linked their grailed profile

            if not user.grailed_handle:
                raise Exception(f"grailed profile is not linked")

            grailed_id = grailed_url.id

            # check if product exists

            product = services.products.get_by_grailed_id(
                db_session=db_session,
                grailed_id=grailed_id,
            )

            if product:
                raise Exception(f"product {product.id} exists")

            # download and parse grailed listing

            code, html_path = services.grailed.download(grailed_id=grailed_id, overwrite=1)

            if code not in [0, 409]:
                raise Exception(f"listing download error {code}")

            grailed_listing = services.grailed.parse_html(html_path=html_path)

            if grailed_listing.code != 0:
                raise Exception(f"listing parse error {grailed_listing.code}")

            if grailed_listing.username != user.grailed_handle:
                raise Exception(f"listing owner does not match")

            name = grailed_listing.title.lower()
            image_urls = grailed_listing.image_urls[0:2]
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

            _code, _image = services.products.images.create(
                db_session=db_session,
                product=product,
                folder=user.ik_folder,
                url=image_url,
            )

        services.products.sync_images(
            db_session=db_session,
            product=product,
        )

        services.products.sync_meta(
            db_session=db_session,
            product=product,
        )

        logger.info(f"{context.rid_get()} product create '{name}' ok - product {product.id}")
    except Exception as e:
        logger.error(f"{context.rid_get()} product create exception '{e}'")
        return fastapi.responses.PlainTextResponse(str(e))

    # product create was successful

    redirect_path = f"/products/{product.id}/edit"

    if "HX-Request" in request.headers:
        response = templates.TemplateResponse(request, "201.html")
        response.headers["HX-Redirect"] = redirect_path
        return response
    else:
        return fastapi.responses.RedirectResponse(redirect_path)


@app.get("/products/{product_id}/images/add", response_class=fastapi.responses.HTMLResponse)
def products_images_add(
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
            folder=user.ik_folder,
            url=image_url,
        )

        if code != 0:
            raise Exception(f"image create error {code}")

        images_error = ""
        logger.info(f"{context.rid_get()} product {product_id} image '{image_url}' add ok")
    except Exception as e:
        images_error = str(e)
        logger.error(f"{context.rid_get()} product {product_id} image add exception '{e}'")
    finally:
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

        thumbnails_map = {
            image.id : services.products.images.transform(product=product, image=image, transform="tr:w-30") for image in images_list
        }
        

    images_count = len(images_list)

    if "HX-Request" in request.headers:
        template = "products/edit_images.html"
    else:
        template = ""

    try:
        response = templates.TemplateResponse(
            request,
            template,
            {
                "images_count": images_count,
                "images_error": images_error,
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


@app.get("/products/{product_id}/images/delete", response_class=fastapi.responses.HTMLResponse)
def products_images_delete(
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

        if product.image_count == 0 and product.state != models.product.STATE_DRAFT:
            # product can not be active without images
            product.state = models.product.STATE_DRAFT

        db_session.add(product)
        db_session.commit()

        # refresh product after image update
        product = services.products.get_by_id(db_session=db_session, id=product.id)

        logger.info(f"{context.rid_get()} product {product_id} image {image_id} delete ok")
    except Exception as e:
        logger.error(f"{context.rid_get()} product {product_id} image {image_id} delete exception '{e}'")

    return fastapi.responses.RedirectResponse(request.headers.get("referer"))


@app.get("/products/{product_id}/links/add", response_class=fastapi.responses.HTMLResponse)
def products_links_add(
    request: fastapi.Request,
    product_id: int,
    link: str,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    logger.info(f"{context.rid_get()} product {product_id} link '{link}' add try")

    try:
        product = services.products.get_by_id(
            db_session=db_session,
            id=product_id,
        )

        services.products.update(
            db_session=db_session,
            product=product,
            data={},
            links=product.links + [link]
        )

        db_session.add(product)
        db_session.commit()

        links_error = ""
        logger.info(f"{context.rid_get()} product {product_id} link '{link}' add ok")
    except Exception as e:
        links_error = str(e)
        logger.error(f"{context.rid_get()} product {product_id} link add exception '{e}'")

    if "HX-Request" in request.headers:
        template = "products/edit_links.html"
    else:
        template = ""
 
    try:
        response = templates.TemplateResponse(
            request,
            template,
            {
                "links_error": links_error,
                "product": product,
                "user": user,
            }
        )
    except Exception as e:
        logger.error(f"{context.rid_get()} product {product_id} link render exception '{e}'")
        return templates.TemplateResponse(request, "500.html", {})

    return response



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

        if product.publishable == 0:
            raise ValueError("product not publishable")

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


@app.get("/products/{product_id}/rembg", response_class=fastapi.responses.HTMLResponse)
def products_rembg(
    request: fastapi.Request,
    product_id: int,
    image_id: int,
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    logger.info(f"{context.rid_get()} product {product_id} image {image_id} rembg try")

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

        r = requests.get(image.url, stream=True)
        if r.status_code != 200:
            raise Exception(f"get request error code {r.status_code}")

        logger.info(f"{context.rid_get()} product {product_id} image {image_id} download starting")

        output_file = f"{image.name}-white.webp"
        output_url = f"file://localhost/{os.getcwd()}/{output_file}"

        input_image = PIL.Image.open(io.BytesIO(r.content))
        input_array = numpy.array(input_image)
        output_array = rembg.remove(input_array, bgcolor=(255, 255, 255, 255))
        output_image = PIL.Image.fromarray(output_array)
        output_image.save(output_file)

        logger.info(f"{context.rid_get()} product {product_id} image {image_id} rembg complete")

        code, _image = services.products.images.create(
            db_session=db_session,
            product=product,
            folder=user.ik_folder,
            url=output_url,
        )

        services.products.sync_images(
            db_session=db_session,
            product=product,
        )

        logger.info(f"{context.rid_get()} product {product_id} image {image_id} upload complete")

        logger.info(f"{context.rid_get()} product {product_id} image {image_id} rembg ok")
    except Exception as e:
        logger.error(f"{context.rid_get()} product {product_id} image {image_id} rembg exception '{e}'")

    return fastapi.responses.RedirectResponse(f"/products/{product_id}/edit")


@app.get("/products/{product_id}/update", response_class=fastapi.responses.PlainTextResponse)
def products_update(
    request: fastapi.Request,
    product_id: int,
    brands: str = "",
    categories: str = "",
    grailed_id: int = 0,
    name: str = "",
    color: str = "",
    link: str = "",
    material: str = "",
    model: str = "",
    season: str = "",
    size: str = "",
    tags: str = "",
    user_id: int = fastapi.Depends(main_shared.get_user_id),
    db_session: sqlmodel.Session = fastapi.Depends(main_shared.get_db),
):
    if user_id == 0:
        return fastapi.responses.RedirectResponse("/login")

    user = services.users.get_by_id(db_session=db_session, id=user_id)

    logger.info(f"{context.rid_get()} product {product_id} update try")

    changes_list = []

    try:
        product = services.products.get_by_id(
            db_session=db_session,
            id=product_id,
        )

        if brands:
            brands_list = [s.strip().lower() for s in brands.split(",") if s]
            product.brands = brands_list
            changes_list.append("brand")

        if categories:
            cats_list = sorted([s.strip().lower() for s in categories.split(",") if s])
            product.categories = cats_list
            changes_list.append("categories")

        if grailed_id:
            product.grailed_id = grailed_id
            changes_list.append("grailed id")

        if link:
            changes_list.append("link")

        if name:
            product.name = name
            changes_list.append("name")

        if tags:
            tags_list = sorted([s.strip().lower() for s in tags.split(",") if s])
            product.tags = tags_list
            changes_list.append("tags")

        # data attributes

        data_mod = product.data
        data_changes = 0

        if color:
            data_mod["color"] = color.lower()
            data_changes += 1
            changes_list.append("color")

        if material:
            data_mod["material"] = material.lower()
            data_changes += 1
            changes_list.append("material")

        if model:
            data_mod["model"] = model.lower()
            data_changes += 1
            changes_list.append("model")

        if season:
            data_mod["season"] = season.lower()
            data_changes += 1
            changes_list.append("season")

        if size:
            data_mod["size"] = size.lower()
            data_changes += 1
            changes_list.append("size")

        if data_changes > 0:
            product.data = data_mod
            sqlalchemy.orm.attributes.flag_modified(product, "data")

        # sync metadata

        services.products.sync_meta(
            db_session=db_session,
            product=product,
        )

        db_session.add(product)
        db_session.commit()

        status_message = ", ".join(changes_list) 
        status_message = f"{status_message} updated"

        logger.info(f"{context.rid_get()} product {product_id} update ok")
    except Exception as e:
        status_message = str(e)
        logger.error(f"{context.rid_get()} product {product_id} update exception '{e}'")

    return fastapi.responses.PlainTextResponse(status_message)
