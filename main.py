import os

import requests

from settings import Settings


def create_dirs(path: str) -> None:
    """Create directories from path if not exists."""
    if not os.path.exists(path):
        os.makedirs(path)


def download_file(url: str, filename: str, mode: str = "wb") -> None:
    """Download file from url."""
    response = requests.get(url=url)
    response.raise_for_status()

    with open(filename, mode) as file:
        file.write(response.content) \
            if mode == "wb" else file.write(response.text)


def main() -> None:
    """ Cli main entrypoint."""
    settings = Settings()
    pathes = (
        os.path.join(settings.ROOT_PATH, settings.IMG_LOGO_PATH),
        os.path.join(settings.ROOT_PATH, settings.BOOK_PATH)
    )
    image_path, book_path = pathes

    for path in pathes:
        create_dirs(path=path)

    download_file(
        url=settings.IMG_URL,
        filename=os.path.join(image_path, settings.IMG_FILENAME)
    )

    download_file(
        url=f"{settings.SITE_URL_ROOT}/{settings.SITE_URI_TXT}",
        filename=os.path.join(book_path, settings.BOOK_FILENAME),
        mode="w"
    )


if __name__ == "__main__":
    main()
