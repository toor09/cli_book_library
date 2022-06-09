from typing import Optional

import requests
from bs4 import BeautifulSoup
from requests import Response

from settings import Settings
from utils import check_for_redirect


def get_post_page(url: str, payload: Optional[dict] = None) -> Response:
    """ Get post page from url."""
    response = requests.get(url=url, params=payload if not None else None)
    response.raise_for_status()
    check_for_redirect(response=response)
    return response


def parse_post_page(page: Response) -> dict:
    """Parse post page and get header, image and text from page."""
    soup = BeautifulSoup(page.text, "lxml")
    post_title = soup.find("main").find("header").find("h1")
    post_image = soup.find("img", class_="attachment-post-image")["src"]
    post_body = soup.find("div", class_="entry-content")

    return {
        "title": post_title.text,
        "text": post_body.text,
        "img": post_image
    }


def main() -> None:
    """Main parser entry."""
    settings = Settings()
    page = get_post_page(url=f"{settings.PARSE_BS4_URL_ROOT}/"
                             f"{settings.PARSE_BS4_URI_BLOG_POST}")
    if page.ok:
        parsed_post = parse_post_page(page=page)

        print(f"{parsed_post.get('title')}\n"
              f"{parsed_post.get('img')}\n"
              f"{parsed_post.get('text')}")


if __name__ == "__main__":
    main()
