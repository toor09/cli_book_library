from pathlib import Path

from pydantic import AnyHttpUrl, BaseSettings


class Settings(BaseSettings):

    IMG_FILENAME: str = "dvmn.svg"
    IMG_LOGO_PATH: Path = Path("img/logo/")
    IMG_URL: AnyHttpUrl
    ROOT_PATH: Path = Path("downloads/")

    class Config:
        case_sensitive = True
        env_file = ".env"
