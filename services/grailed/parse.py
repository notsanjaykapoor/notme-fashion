import dataclasses
import json
import re

import bs4

import models


def parse_html(html_path: str) -> models.GrailedListing:
    """
    Parse grailed listing html file into structured data.
    """
    struct = models.GrailedListing(
        code=0,
        description="",
        image_urls=[],
        userid=0,
        username="",
        title="",
        errors=[]
    )

    soup = bs4.BeautifulSoup(open(html_path), "html.parser")

    # find all main content divs
    div_mains = [div for div in soup.find_all("div") if _tag_attrs_class_match(div.attrs, "maincontent")]

    # get main photo gallery
    div_photos = [div for div in div_mains if _tag_attrs_class_match(div.attrs, "photogallery")]

    if not div_photos:
        struct.code = 422
        struct.errors.append("grailed images not found")
        return struct

    struct.image_urls = _tag_img_list(tag=div_photos[0])

    # get main sidebar
    div_sidebars = [div for div in div_mains if _tag_attrs_class_match(div.attrs, "sidebar")]
    
    if not div_sidebars:
        struct.code = 422
        struct.errors.append("grailed sidebar not found")
        return struct

    div_sidebar = div_sidebars[0]

    # find title
    div_matches = [div for div in div_sidebar.find_all("h1") if _tag_attrs_class_match(div.attrs, "title")]

    if not div_matches:
        struct.code = 422
        struct.errors.append("grailed title not found")
        return struct

    # build title from h1 tag
    h1_tag = div_matches[0]
    struct.title = _tag_text(tag=h1_tag).strip()

    # find description
    div_matches = [div for div in div_sidebar.find_all("div") if _tag_attrs_class_match(div.attrs, "description")]

    if div_matches:
        # build description from child tags
        div_tag = div_matches[0]
        struct.description = " ".join(
            [_tag_text(tag=tag) for tag in div_tag.find_all("p")]
        ).strip()

    # find username in script tag
    script_tags = [tag for tag in soup.find_all("script") if _tag_attrs_type_match(tag.attrs, "application/json")]

    for script_tag in script_tags:
        # iterate and stop on first matching tag
        struct.userid, struct.username = _script_tag_username(tag=script_tag)
        if struct.username:
            break

    return struct


def _script_tag_username(tag: bs4.element.Tag) -> tuple[int, str]:
    """
    Get grailed user id and username from script tag
    """
    try:
        json_data = json.loads(tag.contents[0])
        seller_data = json_data.get("props").get("pageProps").get("listing").get("seller")
        grailed_userid = seller_data.get("id")
        grailed_username = seller_data.get("username")

        return grailed_userid, grailed_username
    except Exception:
        return 0, ""


def _tag_attrs_class_match(attrs: dict, name: str) -> int:
    if name in " ".join(attrs.get("class", [])).lower():
        return 1
    
    return 0


def _tag_attrs_type_match(attrs: dict, name: str) -> int:
    if name in attrs.get("type", "").lower():
        return 1
    
    return 0


def _tag_img_list(tag: bs4.element.Tag) -> list[str]:
    """
    """
    img_tags = tag.find_all("img")

    # use dict here to preserve order
    img_dict = {}

    for tag in img_tags:
        src = tag.attrs.get("src", "")
        if not src:
            continue

        # normalize src url
        if match := re.search(r"(.*)(\?.*)$", src):
            src = match[1]

        img_dict[src] = ""

    return list(img_dict.keys())


def _tag_text(tag: bs4.element.Tag) -> str:
    """
    Get tag contents as a string
    """
    s = " ".join([str(s) for s in tag.contents if type(s) == bs4.element.NavigableString])

    return s
