import json
import os
from dataclasses import dataclass
from datetime import datetime as dt
from functools import partial
from pathlib import Path
from typing import Dict, List, Union

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked
from pathvalidate import sanitize_filepath

from download import create_dirs
from settings import Settings


@dataclass
class PageContext:
    book_cards: List[List[Dict]]
    pages_total: int
    file_path: Union[str, Path]


def build_pages(page: PageContext) -> None:
    """Rebuild pages after edit template.html."""
    for page_number, book_card_chunk in enumerate(page.book_cards, start=1):
        render_page(
            book_cards=book_card_chunk,
            page_number=page_number,
            pages_total=page.pages_total,
            file_path=page.file_path
        )
    print(f"{dt.now()} Pages are rebuilt...")


def render_live(
    book_card_chunks: List[List[Dict]],
    pages_total: int,
    library_file_path: Union[str, Path],
    settings: Settings
) -> None:
    """Auto reloading after edit template.html."""
    page_context = PageContext(
        book_cards=book_card_chunks,
        pages_total=pages_total,
        file_path=library_file_path
    )
    rebuild = partial(build_pages, page_context)
    rebuild()
    server = Server()
    server.watch("static/html/template.html", rebuild)
    server.serve(
        root=".",
        default_filename=f"{settings.LIBRARY_PATH}/index1.html"
    )


def extract_book_cards(file_path: str) -> List[Dict]:
    """Return book_cards from file."""

    with open(file_path, mode="r") as file:
        card_books = (
            card_book
            for card_book in json.load(file)
        )
    return list(card_books)


def render_page(
        book_cards: List[Dict],
        page_number: int,
        pages_total: int,
        file_path: Union[str, Path]
) -> None:
    """Render page with template variables."""

    env = Environment(
        loader=FileSystemLoader("static/html"),
        autoescape=select_autoescape(["html", "xml"])
    )

    template = env.get_template("template.html")

    rendered_page = template.render(
        book_cards=book_cards,
        current_page=page_number,
        pages_total=pages_total
    )
    file_path = f"{file_path}/index{page_number}.html"
    with open(file_path, mode="w", encoding="utf8") as file:
        file.write(rendered_page)


def main() -> None:
    """Render page from books description json file."""

    settings = Settings()
    create_dirs("pages")
    file_path = os.path.join(
        sanitize_filepath(settings.ROOT_PATH),
        sanitize_filepath(settings.DESCRIPTION_FILE)
    )
    library_file_path = sanitize_filepath(settings.LIBRARY_PATH)

    book_cards = extract_book_cards(file_path)
    book_card_chunks = list(chunked(book_cards, settings.PAGE_SIZE))
    pages_total = len(book_card_chunks)

    for page_number, book_card_chunk in enumerate(book_card_chunks, start=1):
        render_page(
            book_cards=book_card_chunk,
            page_number=page_number,
            pages_total=pages_total,
            file_path=library_file_path
        )

    if settings.AUTO_RELOAD:
        render_live(
            book_card_chunks=book_card_chunks,
            pages_total=pages_total,
            library_file_path=library_file_path,
            settings=settings
        )


if __name__ == "__main__":
    main()
