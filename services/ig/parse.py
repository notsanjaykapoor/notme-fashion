import dataclasses
import re

import bs4

import models


def parse_html(html_path: str) -> models.IgPost:
    """
    Parse instagram post html file into structured data.
    """
    struct = models.IgPost(
        code=0,
        description="",
        userid=0,
        username="",
        title="",
        errors=[]
    )

    soup = bs4.BeautifulSoup(open(html_path), "html.parser")

    meta_tags = soup.find_all("meta")

    # meta title tag will have the post title/caption
    # e.g. <meta content='Sanjay Kapoor on Instagram: "#paris #freddys"' property="og:title"/>

    meta_title_tags = [tag for tag in meta_tags if _tag_attrs_prop_match(attrs=tag.attrs, name="og:title")]

    for tag in meta_title_tags:
        title = tag.attrs.get("content")
        struct.title = f"{struct.title} {title}".strip()

    # meta title tag will have the post description, with a formatted string that includes the user ig handle
    # e.g. <meta content='7 likes, 0 comments - swrecked on February 14, 2025: "#paris #freddys". ' property="og:description"/>

    meta_description_tags = [tag for tag in meta_tags if _tag_attrs_prop_match(attrs=tag.attrs, name="og:description")]

    for tag in meta_description_tags:
        struct.username = _username_parse(s=tag.attrs.get("content"))

    return struct


def _username_parse(s: str) -> str:
    match = re.search(r"-\s(\S*)\s", s)
    
    if not match:
        return ""

    return match[1]


def _tag_attrs_prop_match(attrs: dict, name: str) -> int:
    if name in attrs.get("property", "").lower():
        return 1
    
    return 0
