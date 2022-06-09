import os
from typing import Optional
from uuid import uuid1

import requests
from pathvalidate import sanitize_filename, sanitize_filepath
from requests import HTTPError, Response


def check_for_redirect(response: Response) -> None:
    """Check for redirect from target."""
    if response.history:
        raise HTTPError(
            "Запрашиваемого ресурса не существует. "
            "Был произведен редирект на главную страницу."
        )


def create_dirs(path: str) -> None:
    """Create directories from path if not exists."""
    if not os.path.exists(path):
        os.makedirs(path)


def get_unique_id() -> str:
    """Get uuid unique id for filename."""
    uid = str(uuid1().int)[:11]
    return uid


def sanitize_filepath_for_download_txt(
        url: str,
        filename: str,
        folder: Optional[str] = "books/"
) -> str:
    """Return sanitizes filepath for download txt file."""
    response = requests.get(url=url)
    response.raise_for_status()

    if folder:
        sanitized_folder = str(sanitize_filepath(folder))
        sanitized_filename = str(sanitize_filename(filename))
        sanitized_filepath = str(
            os.path.join(sanitized_folder, f"{sanitized_filename}.txt")
        )
    else:
        sanitized_filepath = str(sanitize_filepath(f"{filename}.txt"))

    return sanitized_filepath
