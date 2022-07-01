import json
import os
from typing import Dict, List

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathvalidate import sanitize_filepath

from settings import Settings


def extract_json_data(file_path: str) -> List[Dict]:
    """Return data from json file."""

    load_file = open(file_path, mode="r")
    card_books = (
        card_book
        for card_book in json.load(load_file)
    )
    return list(card_books)


def render_page(card_books: List[Dict]) -> None:
    """Render page with template variables."""

    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(["html", "xml"])
    )

    template = env.get_template("template.html")

    rendered_page = template.render(
        card_books=card_books
    )

    with open("index.html", "w", encoding="utf8") as file:
        file.write(rendered_page)


def main() -> None:
    """Render page from books description json file."""

    settings = Settings()
    file = os.path.join(
        sanitize_filepath(settings.ROOT_PATH),
        sanitize_filepath(settings.DESCRIPTION_FILE)
    )
    card_books = extract_json_data(file)
    render_page(card_books)


if __name__ == "__main__":
    main()
