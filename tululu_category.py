import os
import textwrap
import time
from urllib.parse import unquote, urljoin, urlsplit
from uuid import uuid1

import click
import requests
from pathvalidate import sanitize_filename, sanitize_filepath
from requests import ConnectionError, HTTPError
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import settings
from download import (
    create_description_file,
    create_dirs,
    download_book_cover,
    download_book_txt,
    transform_book_description
)
from parse import (
    check_for_redirect,
    parse_book_links_for_download,
    parse_book_page
)
from settings import Settings


def validate_options(start_page: int, end_page: int) -> None:
    if start_page > end_page:
        raise click.ClickException(
            "Option --end_page must be greater than option --start-page"
        )
    if start_page <= 0:
        raise click.ClickException(
            "Option --start_page must be greater than 0"
        )


@click.command()
@click.option(
    "-s", "--start-page",
    default=1,
    help="From page of book's category."
)
@click.option(
    "-e", "--end-page",
    default=10,
    help="To page of book's category."
)
@click.option(
    "-I", "--skip-imgs",
    default=False,
    help="Skip images downloading."
)
@click.option(
    "-T", "--skip-txt",
    default=False,
    help="Skip book content downloading."
)
@click.option(
    "-J", "--json-path",
    default=".",
    help="Path to generate books description books.json."
)
@click.option(
    "-D", "--dest-folder",
    default=settings.Settings().ROOT_PATH,
    help="Destination path for books downloading."
)
def main(
        start_page: int,
        end_page: int,
        skip_imgs: bool,
        skip_txt: bool,
        json_path: str,
        dest_folder: str
) -> None:
    """Download books and covers, generate book.json."""
    validate_options(start_page=start_page, end_page=end_page)
    settings = Settings()

    if not dest_folder:
        image_path = os.path.join(
            sanitize_filepath(settings.ROOT_PATH),
            sanitize_filepath(settings.IMG_PATH)
        )
        book_path = os.path.join(
            sanitize_filepath(settings.ROOT_PATH),
            sanitize_filepath(settings.BOOK_PATH)
        )
        list(map(create_dirs, (image_path, book_path)))

    else:
        image_path = os.path.join(
            sanitize_filepath(dest_folder, platform="auto"),
            sanitize_filepath(settings.IMG_PATH)
        )
        book_path = os.path.join(
            sanitize_filepath(dest_folder, platform="auto"),
            sanitize_filepath(settings.BOOK_PATH)
        )
        books_desc_path = os.path.join(
            sanitize_filepath(dest_folder, platform="auto"),
            sanitize_filepath(json_path, platform="auto")
        )
        list(map(create_dirs, (image_path, book_path, books_desc_path)))

    retry_strategy = Retry(
        total=settings.RETRY_COUNT,
        status_forcelist=settings.STATUS_FORCE_LIST,
        allowed_methods=settings.ALLOWED_METHODS
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)

    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    books_description = []
    books = []
    for page in range(start_page, end_page + 1):
        try:
            url = urljoin(
                settings.SITE_URL_ROOT,
                f"{settings.CATEGORY_NAME}/{page}/")
            category_page = session.get(url=url)
            category_page.raise_for_status()
            book_links = parse_book_links_for_download(page=category_page)
            book_links = [
                urljoin(settings.SITE_URL_ROOT, book_link)
                for book_link in book_links
            ]
            for book_link in book_links:
                book_id = urlsplit(book_link).path[2:-1]
                book_page = session.get(
                    url=book_link,
                    params={"id": book_id},
                    timeout=settings.TIMEOUT
                )
                book_page.raise_for_status()
                check_for_redirect(response=book_page)

                book_attrs = parse_book_page(page=book_page)
                filename = sanitize_filename(
                    book_attrs.get("title")  # type: ignore
                )
                book_cover_filename = ""
                if not skip_imgs:
                    book_cover_link = unquote(book_attrs.get("img_link") or "")
                    book_cover_title = book_cover_link.split(os.sep)[-1]
                    book_cover_filename = os.path.join(
                        image_path,
                        f"{urlsplit(book_link).path[2:-1]}.{book_cover_title}"
                    )
                    download_book_cover(
                        session=session,
                        url=urljoin(settings.SITE_URL_ROOT, book_cover_link),
                        filename=book_cover_filename
                    )

                book_filename = ""
                if not skip_txt:
                    book_filename = os.path.join(
                        book_path,
                        f"{book_id}.{filename}"
                        f"-{str(uuid1().int)[:11]}.txt"
                    )
                    download_book_txt(
                        session=session,
                        url=urljoin(
                            settings.SITE_URL_ROOT,
                            settings.SITE_URI_TXT
                        ),
                        filename=book_filename,
                        params={"id": book_id}
                    )

                book_attrs.update(
                    {
                        "img_src": book_cover_filename,
                        "book_path": book_filename
                    }
                )
                books_description.append(book_attrs)
                books = transform_book_description(
                    book_attrs=books_description
                )

                message = f"""Книга с id={book_id}
                        c названием `{filename}`
                        была успешно загружена.
                        Название: `{book_attrs.get("title")}`
                        Автор: {book_attrs.get("author")}
                        Жанры: {book_attrs.get("genres")}
                        Отзывы: {book_attrs.get("comments")}
                    """
                message = "\n".join(
                    [textwrap.dedent(line) for line in message.split("\n")]
                )
                click.echo(message)

        except HTTPError as exc:
            click.echo(f"Книга с id={book_id} {exc}")

        except ConnectionError as exc:
            click.echo(f"Ошибка подключения :( {exc}")
            time.sleep(settings.TIMEOUT)

    if not json_path:
        create_description_file(
            filename=os.path.join(
                sanitize_filepath(settings.ROOT_PATH),
                sanitize_filepath(settings.DESCRIPTION_FILE)
            ),
            books_description=books
        )

    elif dest_folder:
        create_description_file(
            filename=os.path.join(
                books_desc_path,
                sanitize_filepath(settings.DESCRIPTION_FILE)
            ),
            books_description=books
        )
    else:
        create_description_file(
            filename=os.path.join(
                books_desc_path,
                sanitize_filepath(json_path, platform="auto"),
                sanitize_filepath(settings.DESCRIPTION_FILE)
            ),
            books_description=books
        )


if __name__ == "__main__":
    main()
