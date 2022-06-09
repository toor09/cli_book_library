import os
from typing import Optional
from uuid import uuid1

import requests
from pathvalidate import sanitize_filename, sanitize_filepath
from requests import HTTPError, Response

from settings import Settings
from tululu import parse_book_page


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


def download_txt(filename: str, response: Response) -> None:
    """Download txt file."""
    with open(filename, "w") as file:
        file.write(response.text)


def _check_for_redirect(response: Response) -> None:
    """Check for redirect from target."""
    if response.history:
        raise HTTPError(
            "Запрашиваемого ресурса не существует. "
            "Был произведен редирект на главную страницу."
        )


def get_page(url: str, payload: Optional[dict] = None) -> Response:
    """Get page from url."""
    response = requests.get(url=url, params=payload if not None else None)
    response.raise_for_status()
    _check_for_redirect(response=response)
    return response


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

    for book_id in range(1, 11):
        try:
            book_page = get_page(
                url=f"{settings.SITE_URL_ROOT}/b{book_id}/",
                payload={"id": book_id}
            )

            if book_page.ok:
                book_attributes = parse_book_page(page=book_page)
                filename = sanitize_filename(str(book_attributes.get("title")))
                txt_file = get_page(
                    url=f"{settings.SITE_URL_ROOT}/{uri_txt}",
                    payload={"id": book_id}
                )
                if txt_file.ok:
                    download_txt(
                        filename=os.path.join(
                            book_path,
                            f"{book_id}. {filename}-{get_unique_id()}.txt"
                        ),
                        response=txt_file
                    )
                    print(f"Книга с id={book_id} и названием {filename}"
                          f" была успешно загружена.")

        except HTTPError as exc:
            print(f"Книга с id={book_id} {exc}")
            continue


if __name__ == "__main__":
    main()
