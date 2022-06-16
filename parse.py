from typing import List

from bs4 import BeautifulSoup
from requests import HTTPError, Response


def check_for_redirect(response: Response) -> None:
    """Check for redirect from target."""
    if response.history:
        raise HTTPError(
            "Запрашиваемого ресурса не существует. "
            "Загрузка невозможна :(.\n"
        )


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


def parse_book_links_for_download(page: Response) -> List[str]:
    """Parse book links from book cards for downloading."""
    soup = BeautifulSoup(page.text, "lxml")
    book_categories = soup.select("#content table.d_book")
    book_links = [
        book.select_one("a")["href"] for book in book_categories
    ]
    return book_links
