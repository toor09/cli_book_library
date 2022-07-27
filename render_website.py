import json
import os
from datetime import datetime as dt
from pathlib import Path
from typing import Dict, List, Union

from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked
from pathvalidate import sanitize_filepath

from download import create_dirs
from settings import Settings


def livereload(
        book_card_chunks: List[List[Dict]],
        total_pages: int,
        library_file_path: Union[str, Path],
        settings: Settings
) -> None:
    """Auto reloading after edit template.html."""

    from livereload import Server

    def rebuild() -> None:
        for number_page, book_card_chunk in enumerate(book_card_chunks):
            render_page(
                book_cards=book_card_chunk,
                number_page=number_page + 1,
                total_pages=total_pages,
                file_path=library_file_path
            )
        print(f"{dt.now()} Pages are rebuilt...")

    rebuild()

    server = Server()
    server.watch("static/html/template.html", rebuild)
    server.serve(
        root=".",
        default_filename=f"{settings.LIBRARY_PATH}/index1.html"
    )


def extract_json_data(file_path: str) -> List[Dict]:
    """Return data from json file."""

    load_file = open(file_path, mode="r")
    card_books = (
        card_book
        for card_book in json.load(load_file)
    )
    return list(card_books)


def render_page(
        book_cards: List[Dict],
        number_page: int,
        total_pages: int,
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
        current_page=number_page,
        total_pages=total_pages
    )
    path_file = f"{file_path}/index{number_page}.html"
    with open(path_file, mode="w", encoding="utf8") as file:
        file.write(rendered_page)


def main() -> None:
    """Render page from books description json file."""

    settings = Settings()
    create_dirs("pages")
    filepath = os.path.join(
        sanitize_filepath(settings.ROOT_PATH),
        sanitize_filepath(settings.DESCRIPTION_FILE)
    )
    library_file_path = sanitize_filepath(settings.LIBRARY_PATH)

    book_cards = extract_json_data(filepath)
    book_card_chunks = list(chunked(book_cards, settings.PAGE_SIZE))
    total_pages = len(book_card_chunks)

    for number_page, book_card_chunk in enumerate(book_card_chunks):
        render_page(
            book_cards=book_card_chunk,
            number_page=number_page + 1,
            total_pages=total_pages,
            file_path=library_file_path
        )

    if settings.AUTO_RELOAD:
        livereload(
            book_card_chunks=book_card_chunks,
            total_pages=total_pages,
            library_file_path=library_file_path,
            settings=settings
        )


if __name__ == "__main__":
    main()
