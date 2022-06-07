import os

import requests

from settings import Settings


def create_dirs(path: str) -> None:
    """Create directories from path if not exists."""
    if not os.path.exists(path):
        os.makedirs(path)


def download_file(url: str, filename: str) -> None:
    """Download file from url."""
    response = requests.get(url=url)
    response.raise_for_status()

    with open(filename, "wb") as file:
        file.write(response.content)


def main() -> None:
    """ Cli main entrypoint."""
    settings = Settings()
    path_dirs = os.path.join(settings.ROOT_PATH, settings.IMG_LOGO_PATH)
    create_dirs(path=path_dirs)
    download_file(
        url=settings.IMG_URL,
        filename=os.path.join(path_dirs, settings.IMG_FILENAME)
    )


if __name__ == "__main__":
    main()
