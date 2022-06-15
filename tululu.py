import os
import textwrap
import time
from urllib.parse import unquote, urljoin
from uuid import uuid1

import click
import requests
from pathvalidate import sanitize_filename, sanitize_filepath
from requests import ConnectionError, HTTPError
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from download import create_dirs, download_book_cover, download_book_txt
from parse import check_for_redirect, parse_book_page
from settings import Settings


def validate_options(start_id: int, end_id: int) -> None:
    if start_id > end_id:
        raise click.ClickException(
            "Option --end-id must be greater than option --start-id"
        )
    if start_id <= 0:
        raise click.ClickException(
            "Option --start-id must be greater than 0"
        )


@click.command()
@click.option(
    "-s", "--start-id",
    default=1,
    help="From id book."
)
@click.option(
    "-e", "--end-id",
    default=10,
    help="To id book."
)
def main(start_id: int, end_id: int) -> None:
    """
    Download books and covers from tululu.org.
    """
    validate_options(start_id, end_id)
    settings = Settings()
    image_path = os.path.join(
        sanitize_filepath(settings.ROOT_PATH),
        sanitize_filepath(settings.IMG_PATH)
    )
    book_path = os.path.join(
        sanitize_filepath(settings.ROOT_PATH),
        sanitize_filepath(settings.BOOK_PATH)
    )

    retry_strategy = Retry(
        total=settings.RETRY_COUNT,
        status_forcelist=settings.STATUS_FORCE_LIST,
        allowed_methods=settings.ALLOWED_METHODS
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)

    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    list(map(create_dirs, (image_path, book_path)))

    for book_id in range(start_id, end_id + 1):
        try:
            book_page = session.get(
                url=f"{settings.SITE_URL_ROOT}/b{book_id}/",
                params={"id": book_id},
                timeout=settings.TIMEOUT
            )
            book_page.raise_for_status()
            check_for_redirect(response=book_page)

            book_attrs = parse_book_page(page=book_page)
            filename = sanitize_filename(
                book_attrs.get("title")  # type: ignore
            )

            book_cover_link = unquote(book_attrs.get("img_link") or "")
            book_cover_title = book_cover_link.split(os.sep)[-1]
            book_cover_filename = os.path.join(
                image_path, f"{book_id}.{book_cover_title}"
            )
            download_book_cover(
                session=session,
                url=urljoin(settings.SITE_URL_ROOT, book_cover_link),
                filename=book_cover_filename
            )

            book_filename = os.path.join(
                book_path,
                f"{book_id}.{filename}-{str(uuid1().int)[:11]}.txt"
            )
            download_book_txt(
                session=session,
                url=urljoin(settings.SITE_URL_ROOT, settings.SITE_URI_TXT),
                filename=book_filename,
                params={"id": book_id}
            )

            message = f"""Книга с id={book_id} c названием `{filename}`
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


if __name__ == "__main__":
    main()
