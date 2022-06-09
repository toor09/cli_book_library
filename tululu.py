from bs4 import BeautifulSoup
from requests import HTTPError, Response

from bs4_tutorial import get_post_page
from settings import Settings


def parse_book_page(page: Response) -> dict:
    """Parse info from book page."""
    soup = BeautifulSoup(page.text, "lxml")
    book_header = soup.find("h1")
    book_cover = soup.find(
        "div", class_="bookimage"
    ).find("a").find("img")["src"]
    book_title, book_author = book_header.text.split("::")

    return {
        "author": book_author.strip(),
        "title": book_title.strip(),
        "img_link": book_cover
    }


def main() -> None:
    """Main entry."""
    settings = Settings()

    for book_id in range(1, 11):
        try:
            book_page = get_post_page(
                url=f"{settings.SITE_URL_ROOT}/b{book_id}/",
                payload={"id": book_id})

            if book_page.ok:
                parsed_book = parse_book_page(page=book_page)

                print(f"Заголовок: {parsed_book.get('title')}\n"
                      f"Автор: {parsed_book.get('author')}\n"
                      f"Ссылка на обложку: {settings.SITE_URL_ROOT}"
                      f"{parsed_book.get('img_link')}")

        except HTTPError as exc:
            print(f"Книга с id={book_id} {exc}")
            continue


if __name__ == "__main__":
    main()