import re


def file_uri_parse(source_uri: str) -> tuple[str, str, str]:
    """
    Parse a file uri into its component parts.

    example file uri - file:///users/notme/foo/bar.txt is parsed into components:

    path - /users/notme/foo/bar.txt
    dir - /users/notme/foo/
    file - bar.txt
    """
    if not (match := re.match(r'^file:\/\/(\/.+)$', source_uri)):
        return "", "", ""

    source_path = match[1]

    match = re.match(r'^(.+)\/([^\/]*)$', source_path)
    source_dir = f"{match[1]}/"
    source_file = match[2]

    return source_path, source_dir, source_file

