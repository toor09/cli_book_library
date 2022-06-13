import os
import textwrap
from urllib.parse import unquote
from uuid import uuid1

import click
import requests
from pathvalidate import sanitize_filename, sanitize_filepath
from requests import ConnectionError, HTTPError
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from download import create_dirs, create_image, create_txt
from parse import _check_for_redirect, parse_book_page
from settings import Settings


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
            _check_for_redirect(response=book_page)
            if book_page.ok:
                book_attrs = parse_book_page(page=book_page)
                filename = sanitize_filename(
                    f"{book_attrs.get('title')}"
                )

                img_link = unquote(book_attrs.get("img_link") or "")
                img_title = img_link.split(os.sep)[-1]

                img_file = session.get(
                    url=f"{settings.SITE_URL_ROOT}/{img_link}"
                )
                img_file.raise_for_status()
                _check_for_redirect(response=img_file)

                if img_file.ok:
                    img_filename = os.path.join(
                        image_path, f"{book_id}.{img_title}"
                    )
                    create_image(filename=img_filename, response=img_file)

                else:
                    click.echo(f"Обложка книги с id={book_id} не была скачана"
                               f" по причине: {img_file.reason}"
                               )

                txt_file = session.get(
                    url=f"{settings.SITE_URL_ROOT}/{settings.SITE_URI_TXT}",
                    params={"id": book_id}
                )
                txt_file.raise_for_status()
                _check_for_redirect(response=txt_file)

                if txt_file.ok:
                    txt_filename = os.path.join(
                        book_path,
                        f"{book_id}.{filename}-{str(uuid1().int)[:11]}.txt"
                    )
                    create_txt(filename=txt_filename, response=txt_file)

                else:
                    click.echo(f"Содержимое книги с id={book_id} не была "
                               f"скачано по причине: {txt_file.reason}"
                               )
                message = f"""Книга с id={book_id} c названием `{filename}`
                        была успешно загружена.
                        Название: `{book_attrs.get('title')}`
                        Автор: {book_attrs.get('author')}
                        Жанры: {book_attrs.get('genres')}
                        Отзывы: {book_attrs.get('comments')}
                """
                message = "\n".join(
                    [textwrap.dedent(line) for line in message.split('\n')]
                )
                click.echo(message)

            else:
                click.echo(f"Страница книги с id={book_id} не доступна по"
                           f" причине: {book_page.reason}"
                           )

        except HTTPError as exc:
            click.echo(f"Книга с id={book_id} {exc}")
            continue

        except ConnectionError as exc:
            click.echo(f"Ошибка подключения :( {exc}")
            continue


if __name__ == "__main__":
    main()
