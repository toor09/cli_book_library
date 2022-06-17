import json
import os
from typing import List, Optional

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


def transform_book_description(
        book_attrs: List[dict],
) -> List[dict]:
    """ Transform book attributes for required view."""
    books_description = []
    for book in book_attrs:
        books_description.append(
            {
                "title": book.get("title"),
                "author": book.get("author"),
                "img_src": book.get("img_src"),
                "book_path": book.get("book_path"),
                "comments": book.get("comments").split("\n"),  # type: ignore
                "genres": book.get("genres")
            }
        )

    return books_description


def create_description_file(
        filename: str,
        books_description: List[dict]
) -> None:
    """Create description file for local library."""
    with open(file=filename, mode="w") as file:
        json.dump(books_description, file, ensure_ascii=False, indent=2)
