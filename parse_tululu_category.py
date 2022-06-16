from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from settings import Settings


def parse_book_url_for_download() -> None:
    """Parse book link from book page for download."""
    settings = Settings()

    book_page = requests.get(url=urljoin(settings.SITE_URL_ROOT, "l55"))
    book_page.raise_for_status()

    soup = BeautifulSoup(book_page.text, "lxml")
    book_uri = soup.find("table", class_="d_book").find("a")["href"]
    book_url = urljoin(settings.SITE_URL_ROOT, book_uri)
    print(f"{book_url=}")


if __name__ == "__main__":
    parse_book_url_for_download()
