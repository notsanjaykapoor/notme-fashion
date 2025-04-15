import os
import subprocess

import services.grailed


def download(grailed_id: int, overwrite: int) -> tuple[int, str]:
    """
    Download grailed listing to local filesystem.
    """
    grailed_url = services.grailed.listing_url(id=grailed_id)
    html_path = f"grailed_{grailed_id}.html"

    if overwrite == 0 and os.path.exists(html_path):
        # file exists and do not overwrite was specified
        return 409, html_path

    response = subprocess.run(
        f"curl --location {grailed_url} > {html_path}",
        shell=True,
        capture_output=False,
    )

    if response.returncode != 0:
        return response.returncode, ""

    return 0, html_path
