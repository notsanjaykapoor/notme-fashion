import dataclasses

import bs4

@dataclasses.dataclass
class Struct:
    code: int
    description: str
    image_urls: list[str]
    name: str
    errors: list[str]


def parse(html_path: str) -> Struct:
    """
    """
    struct = Struct(
        code=0,
        description="",
        image_urls=[],
        name="",
        errors=[]
    )

    soup = bs4.BeautifulSoup(open(html_path), "html.parser")

    # find all main content divs
    # div_mains = soup.find_all("div", class_=re.compile("MainContent", re.IGNORECASE))
    div_mains = [div for div in soup.find_all("div") if _div_attrs_class_match(div.attrs, "maincontent")]

    # get main photo gallery
    div_photos = [div for div in div_mains if _div_attrs_class_match(div.attrs, "photogallery")]

    if not div_photos:
        struct.code = 422
        struct.errors.append("grailed images not found")
        return struct

    struct.image_urls = _img_list(tag=div_photos[0])

    # get main sidebar
    div_sidebars = [div for div in div_mains if _div_attrs_class_match(div.attrs, "sidebar")]
    
    if not div_sidebars:
        struct.code = 422
        struct.errors.append("grailed sidebar not found")
        return struct

    div_sidebar = div_sidebars[0]

    # find title
    div_matches = [div for div in div_sidebar.find_all("h1") if _div_attrs_class_match(div.attrs, "title")]

    if not div_matches:
        struct.code = 422
        struct.errors.append("grailed title not found")
        return struct

    # build title from h1 tag
    h1_tag = div_matches[0]
    struct.name = _tag_text(tag=h1_tag).strip()

    # find description
    div_matches = [div for div in div_sidebar.find_all("div") if _div_attrs_class_match(div.attrs, "description")]

    if div_matches:
        # build description from child tags
        div_tag = div_matches[0]
        struct.description = " ".join(
            [_tag_text(tag=tag) for tag in div_tag.find_all("p")]
        ).strip()

    return struct


def _div_attrs_class_match(attrs: dict, name: str) -> int:
    if name in " ".join(attrs.get("class", [])).lower():
        return 1
    
    return 0


def _tag_text(tag: bs4.element.Tag) -> str:
    """
    Get tag contents as a string
    """
    s = " ".join([str(s) for s in tag.contents if type(s) == bs4.element.NavigableString])

    return s


def _img_list(tag: bs4.element.Tag) -> list[str]:
    """
    """
    img_tags = tag.find_all("img")

    # use dict here to preserve order
    img_dict = {}

    for tag in img_tags:
        src = tag.attrs.get("src", "")
        if not src:
            continue
        img_dict[src] = ""

    return list(img_dict.keys())
