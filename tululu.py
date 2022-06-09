from bs4 import BeautifulSoup
from requests import Response

from bs4_tutorial import get_post_page
from settings import Settings


def parse_book_page(page: Response) -> dict:
    """Parse info from book page."""
    soup = BeautifulSoup(page.text, "lxml")
    book_header = soup.find("h1")
    book_title, book_author = book_header.text.split("::")
    return {
        "author": book_author.strip(),
        "title": book_title.strip()
    }


def main() -> None:
    """Main entry."""
    settings = Settings()
    page = get_post_page(url=settings.BOOK_PAGE)

    if page.ok:
        parsed_book = parse_book_page(page=page)

        print(f"Заголовок: {parsed_book.get('title')}\n"
              f"Автор: {parsed_book.get('author')}")


if __name__ == "__main__":
    main()
