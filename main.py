import os
from typing import Optional

import requests
from requests import HTTPError, Response

from settings import Settings


def create_dirs(path: str) -> None:
    """Create directories from path if not exists."""
    if not os.path.exists(path):
        os.makedirs(path)


def _check_for_redirect(response: Response) -> None:
    """Check for redirect from target."""
    if response.history:
        raise HTTPError(
            "Запрашиваемого ресурса не существует. "
            "Был произведен редирект на главную страницу."
        )


def download_image_file(url: str, filename: str) -> None:
    """Download image file from url."""
    response = requests.get(url=url)
    response.raise_for_status()

    with open(filename, "wb") as file:
        file.write(response.content)


def download_txt_file(
        url: str,
        filename: str,
        payload: Optional[dict] = None
) -> None:
    """Download txt file from url."""
    response = requests.get(url=url, params=payload if not None else None)
    response.raise_for_status()
    _check_for_redirect(response=response)

    with open(filename, "w") as file:
        file.write(response.text)


def main() -> None:
    """ Cli main entrypoint."""
    settings = Settings()
    uri_txt = settings.SITE_URI_TXT.split("?")[0]
    image_path, book_path = (
        os.path.join(settings.ROOT_PATH, settings.IMG_LOGO_PATH),
        os.path.join(settings.ROOT_PATH, settings.BOOK_PATH)
    )

    list(map(create_dirs, (image_path, book_path)))

    download_image_file(
        url=settings.IMG_URL,
        filename=os.path.join(image_path, settings.IMG_FILENAME)
    )

    download_txt_file(
        url=f"{settings.SITE_URL_ROOT}/{settings.SITE_URI_TXT}",
        filename=os.path.join(book_path, settings.BOOK_FILENAME)
    )

    for book_id in range(1, 11):
        try:
            download_txt_file(
                url=f"{settings.SITE_URL_ROOT}/{uri_txt}",
                filename=os.path.join(book_path, f"id{book_id}.txt"),
                payload={"id": book_id}
            )
            print(f"Книга с id={book_id} была успешно загружена.")

        except HTTPError as exc:
            print(f"Книга с id={book_id} {exc}")
            continue


if __name__ == "__main__":
    main()
