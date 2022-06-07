from pathlib import Path

from pydantic import AnyHttpUrl, BaseSettings


class Settings(BaseSettings):

    BOOK_FILENAME: str = "arthur_clarke-sands_of_mars.txt"
    BOOK_PATH: Path = Path("books")
    IMG_FILENAME: str = "dvmn.svg"
    IMG_LOGO_PATH: Path = Path("img/logo/")
    IMG_URL: AnyHttpUrl
    ROOT_PATH: Path = Path("downloads/")
    SITE_URL_ROOT: AnyHttpUrl
    SITE_URI_TXT: str

    class Config:
        case_sensitive = True
        env_file = ".env"
