import os
from typing import Optional

import requests
from pathvalidate import sanitize_filename, sanitize_filepath
from requests import HTTPError, Response

from settings import Settings


def create_dirs(path: str) -> None:
    """Create directories from path if not exists."""
    if not os.path.exists(path):
        os.makedirs(path)


def _sanitize_filepath_for_download_txt(
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


def _check_for_redirect(response: Response) -> None:
    """Check for redirect from target."""
    if response.history:
        raise HTTPError(
            "Запрашиваемого ресурса не существует. "
            "Был произведен редирект на главную страницу."
        )


def download_image_file(
        url: str,
        filename: str
) -> None:
    """Download image file from url."""
    response = requests.get(url=url)
    response.raise_for_status()

    filename = str(sanitize_filepath(filename))
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
        os.path.join(
            sanitize_filepath(settings.ROOT_PATH),
            sanitize_filepath(settings.IMG_LOGO_PATH)
        ),
        os.path.join(
            sanitize_filepath(settings.ROOT_PATH),
            sanitize_filepath(settings.BOOK_PATH)
        )
    )

    list(map(create_dirs, (image_path, book_path)))

    download_image_file(
        url=settings.IMG_URL,
        filename=os.path.join(
            image_path,
            sanitize_filename(settings.IMG_FILENAME)
        )
    )

    download_txt_file(
        url=f"{settings.SITE_URL_ROOT}/{settings.SITE_URI_TXT}",
        filename=os.path.join(
            book_path,
            sanitize_filename(settings.BOOK_FILENAME)
        )
    )

    for book_id in range(1, 11):
        try:
            download_txt_file(
                url=f"{settings.SITE_URL_ROOT}/{uri_txt}",
                filename=os.path.join(
                    book_path,
                    sanitize_filename(f"id{book_id}.txt")
                ),
                payload={"id": book_id}
            )
            print(f"Книга с id={book_id} была успешно загружена.")

        except HTTPError as exc:
            print(f"Книга с id={book_id} {exc}")
            continue

    urls = [f"{settings.SITE_URL_ROOT}/{settings.SITE_URI_TXT}"
            for _ in range(3)]
    filenames = ["Алиби", "Али/би", "Али\\би"]
    folders = ["books/", "txt/"]

    sanitized_pathes = list(map(
        _sanitize_filepath_for_download_txt, urls, filenames, folders)
    )
    print(f"{sanitized_pathes=}")
    list(map(create_dirs, folders))
    list(map(download_txt_file, urls, sanitized_pathes))


if __name__ == "__main__":
    main()
