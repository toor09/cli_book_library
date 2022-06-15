import os
from typing import Optional

from requests import Session

from parse import check_for_redirect


def create_dirs(path: str) -> None:
    """Create directories from path if not exists."""
    if not os.path.exists(path):
        os.makedirs(path)


def download_book_cover(session: Session, url: str, filename: str) -> None:
    """ Download book cover from current page."""
    book_cover = session.get(url=url)
    book_cover.raise_for_status()
    check_for_redirect(response=book_cover)

    with open(file=filename, mode="wb") as file:
        file.write(book_cover.content)


def download_book_txt(
        session: Session,
        url: str,
        filename: str,
        params: Optional[dict] = None
) -> None:
    """ Download book content from current page."""
    book_txt = session.get(url=url, params=params if params else None)
    book_txt.raise_for_status()
    check_for_redirect(response=book_txt)

    with open(file=filename, mode="w") as file:
        file.write(book_txt.text)
