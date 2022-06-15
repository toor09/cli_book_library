from typing import Optional

import requests
from bs4 import BeautifulSoup
from requests import HTTPError, Response


def check_for_redirect(response: Response) -> None:
    """Check for redirect from target."""
    if response.history:
        raise HTTPError(
            "Запрашиваемого ресурса не существует. "
            "Загрузка невозможна :(.\n"
        )


def get_book_cover(session: requests.Session, url: str) -> Response:
    """ Get book cover from current page."""
    img_content = session.get(url=url)
    img_content.raise_for_status()
    check_for_redirect(response=img_content)
    return img_content


def get_book_content(
        session: requests.Session,
        url: str,
        params: Optional[dict] = None
) -> Response:
    """ Get book content from current page."""
    txt_content = session.get(url=url, params=params if params else None)
    txt_content.raise_for_status()
    check_for_redirect(response=txt_content)
    return txt_content


def parse_book_page(page: Response) -> dict:
    """Parse info from book page."""
    soup = BeautifulSoup(page.text, "lxml")
    book_title, book_author = soup.find("h1").text.split("::")
    book_cover = soup.find(
        "div", class_="bookimage"
    ).find("a").find("img")["src"]
    book_comments = soup.find_all("div", class_="texts")
    book_comments = [
        book_comment.find_next("span", class_="black").text.strip()
        for book_comment in book_comments
    ]
    book_comments = "\n".join(book_comments)
    book_genres = [
        book_genre.text.strip()
        for book_genre in soup.find("span", class_="d_book").find_all("a")
    ]

    return {
        "author": book_author.strip(),
        "title": book_title.strip(),
        "img_link": book_cover,
        "genres": book_genres,
        "comments": book_comments or "Еще нет отзывов"
    }
