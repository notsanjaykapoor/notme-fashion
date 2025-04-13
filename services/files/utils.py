import re


def file_uri_parse(source_uri: str) -> tuple[str, str, str]:
    """
    Parse a file uri into its component parts.

    example file uri - file:///localhost/users/notme/foo/bar.txt
    """
    if not (match := re.match(r'^file:\/\/([^\/]+)\/(.+)$', source_uri)):
        raise ValueError(f"invalid source_uri {source_uri}")

    source_host, source_path = (match[1], match[2])

    match = re.match(r'^(.+)\/([^\/]*)$', source_path)
    source_dir = f"{match[1]}/"
    source_file = match[2]

    return source_host, source_dir, source_file