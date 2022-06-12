import os
from urllib.parse import unquote

import click
import requests
from pathvalidate import sanitize_filename, sanitize_filepath
from requests import HTTPError

from download import create_dirs, download_image, download_txt
from parse import _check_for_redirect, parse_book_page
from settings import Settings
from utils import get_unique_id


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

    list(map(create_dirs, (image_path, book_path)))

    for book_id in range(start_id, end_id + 1):
        try:
            book_page = requests.get(
                url=f"{settings.SITE_URL_ROOT}/b{book_id}/",
                params={"id": book_id}
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

                img_file = requests.get(
                    url=f"{settings.SITE_URL_ROOT}/{img_link}"
                )
                img_file.raise_for_status()
                _check_for_redirect(response=img_file)

                if img_file.ok:
                    img_filename = os.path.join(
                        image_path, f"{book_id}.{img_title}"
                    )
                    download_image(filename=img_filename, response=img_file)

                else:
                    click.echo(f"Обложка книги с id={book_id} не была скачана"
                               f" по причине: {img_file.reason}"
                               )

                txt_file = requests.get(
                    url=f"{settings.SITE_URL_ROOT}/{settings.SITE_URI_TXT}",
                    params={"id": book_id}
                )
                txt_file.raise_for_status()
                _check_for_redirect(response=txt_file)

                if txt_file.ok:
                    txt_filename = os.path.join(
                        book_path,
                        f"{book_id}.{filename}-{get_unique_id()}.txt"
                    )
                    download_txt(filename=txt_filename, response=txt_file)

                else:
                    click.echo(f"Содержимое книги с id={book_id} не была "
                               f"скачано по причине: {txt_file.reason}"
                               )

                click.echo(
                    f"Книга с id={book_id} c названием `{filename}` "
                    f"была успешно загружена.\n"
                    f"Название: `{book_attrs.get('title')}`\n"
                    f"Автор: {book_attrs.get('author')}\n"
                    f"Жанры: {book_attrs.get('genres')}\n"
                    f"Отзывы: {book_attrs.get('comments')}\n"
                )

            else:
                click.echo(f"Страница книги с id={book_id} не доступна по"
                           f" причине: {book_page.reason}"
                           )

        except HTTPError as exc:
            click.echo(f"Книга с id={book_id} {exc}")
            continue


if __name__ == "__main__":
    main()
