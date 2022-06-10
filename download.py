import os

from requests import Response


def create_dirs(path: str) -> None:
    """Create directories from path if not exists."""
    if not os.path.exists(path):
        os.makedirs(path)


def download_txt(filename: str, response: Response) -> None:
    """Download txt file."""
    with open(filename, "w") as file:
        file.write(response.text)


def download_image(filename: str, response: Response) -> None:
    """Download image file."""
    with open(filename, "wb") as file:
        file.write(response.content)
