import os

from requests import Response


def create_dirs(path: str) -> None:
    """Create directories from path if not exists."""
    if not os.path.exists(path):
        os.makedirs(path)


def create_txt(filename: str, response: Response) -> None:
    """Create txt file."""
    with open(filename, "w") as file:
        file.write(response.text)


def create_image(filename: str, response: Response) -> None:
    """Create image file."""
    with open(filename, "wb") as file:
        file.write(response.content)
