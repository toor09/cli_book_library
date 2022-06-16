from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from settings import Settings


def parse_book_links_for_download() -> None:
    """Parse book links from book cards for download."""
    settings = Settings()
    for page in range(1, 11):
        book_page = requests.get(
            url=urljoin(settings.SITE_URL_ROOT, f"l55/{page}/")
        )
        book_page.raise_for_status()

        soup = BeautifulSoup(book_page.text, "lxml")
        book_cards = soup.find(
            id="content"
        ).find_all("table", class_="d_book")
        book_links = [
            book_card.find_next("a")["href"] for book_card in book_cards
        ]

        for book_link in book_links:
            print(urljoin(settings.SITE_URL_ROOT, book_link))


if __name__ == "__main__":
    parse_book_links_for_download()
