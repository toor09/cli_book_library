from pathlib import Path

from pydantic import AnyHttpUrl, BaseSettings


class Settings(BaseSettings):

    ROOT_PATH: Path = Path("downloads")
    BOOK_PATH: Path = Path("books")
    IMG_PATH: Path = Path("img")
    SITE_URL_ROOT: AnyHttpUrl
    SITE_URI_TXT: str

    class Config:
        case_sensitive = True
        env_file = ".env"
