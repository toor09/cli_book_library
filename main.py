import os
from typing import Optional
from urllib.parse import unquote

import requests
from pathvalidate import sanitize_filename, sanitize_filepath
from requests import HTTPError, Response

from settings import Settings
from tululu import parse_book_page
from utils import check_for_redirect, create_dirs, get_unique_id


def download_image_file(
        url: str,
        filename: str
) -> None:
    """Download image file from url."""
    response = requests.get(url=url)
    response.raise_for_status()
    check_for_redirect(response=response)

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
    check_for_redirect(response=response)

    with open(filename, "w") as file:
        file.write(response.text)


def download_txt(filename: str, response: Response) -> None:
    """Download txt file."""
    with open(filename, "w") as file:
        file.write(response.text)


def download_image(filename: str, response: Response) -> None:
    """Download image file."""
    with open(filename, "wb") as file:
        file.write(response.content)


def get_page(url: str, payload: Optional[dict] = None) -> Response:
    """Get page from url."""
    response = requests.get(url=url, params=payload if not None else None)
    response.raise_for_status()
    check_for_redirect(response=response)
    return response


def main() -> None:
    """ Cli main entrypoint."""
    settings = Settings()
    uri_txt = settings.SITE_URI_TXT.split("?")[0]
    image_path, book_path = (
        os.path.join(
            sanitize_filepath(settings.ROOT_PATH),
            sanitize_filepath(settings.IMG_PATH)
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
                filename = sanitize_filename(
                    str(book_attributes.get("title"))
                )
                img_link = book_attributes.get("img_link") or ""
                img_link = unquote(img_link)
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
                img_file = get_page(
                    url=f"{settings.SITE_URL_ROOT}/{img_link}"
                )
                img_title = img_link.split(os.sep)[-1]
                if img_file.ok:
                    download_image(
                        filename=os.path.join(
                            image_path,
                            f"{book_id}.{img_title}"
                        ),
                        response=img_file
                    )

                print(f"Книга с id={book_id} и названием {filename} "
                      f"была успешно загружена.")

        except HTTPError as exc:
            print(f"Книга с id={book_id} {exc}")
            continue


if __name__ == "__main__":
    main()
