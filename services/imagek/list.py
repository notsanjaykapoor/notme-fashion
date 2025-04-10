import dataclasses

import imagekitio.models.ListAndSearchFileRequestOptions

import services.imagek


@dataclasses.dataclass
class Struct:
    code: int
    objects: list[dict]
    count: int
    total: int
    errors: list[str]


def list(path: str, type: str, query: str="", offset: int=0, limit: int=5) -> Struct:
    """
    """
    struct = Struct(
        code=0,
        objects=[],
        count=0,
        total=0,
        errors=[],
    )

    client = services.imagek.client()

    # docs: https://imagekit.io/docs/api-reference/digital-asset-management-dam/list-and-search-assets#list-and-search-file-api
    options = imagekitio.models.ListAndSearchFileRequestOptions.ListAndSearchFileRequestOptions(
        file_type="all",
        limit=limit,
        path=path,
        skip=offset,
        sort="ASC_CREATED",
        tags="",
        type=type, # all, file, file-version, folder
    )

    result = client.list_files(options=options)

    struct.objects = result.response_metadata.raw
    struct.count = len(struct.objects)

    return struct

