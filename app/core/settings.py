from pydantic_settings import BaseSettings
from functools import cached_property
from app.utils.llm import ModelLoader
from typing import ClassVar
from pathlib import Path
from typing import List, Dict


class Settings(BaseSettings):
    APP_ENV: str = "local"
    INTERNAL_AUTH_TOKEN: str
    DB_NAMES: str

    DB_CONNECTION: str
    DB_HOST: str
    DB_PORT: int
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_DATABASE: str

    BASE_DIR: ClassVar[Path] = Path(__file__).resolve().parent.parent
    ROOT_DIR: ClassVar[Path] = BASE_DIR.parent
    GEMMA_PATH: ClassVar[Path] = ROOT_DIR / "public" / "model"

    @cached_property
    def db_names(self) -> List[str]:
        return [x.strip() for x in self.DB_NAMES.split(",")]

    def get_db_configs(self) -> Dict[str, dict]:
        dbs = {}
        for idx, name in enumerate(self.db_names):
            suffix = "" if idx == 0 else str(idx + 1)
            dbs[name] = {
                "driver": getattr(self, f"DB_CONNECTION{suffix}", None),
                "host": getattr(self, f"DB_HOST{suffix}", None),
                "port": getattr(self, f"DB_PORT{suffix}", None),
                "user": getattr(self, f"DB_USERNAME{suffix}", None),
                "password": getattr(self, f"DB_PASSWORD{suffix}", None),
                "db": getattr(self, f"DB_DATABASE{suffix}", None),
            }
        return dbs

    def get_db_url(self, db_name: str, sync: bool = False) -> str:
        config = self.get_db_configs()[db_name]
        base_driver = config["driver"]

        if not base_driver:
            raise ValueError(f"Driver tidak ditemukan untuk {db_name}")
        if base_driver == "mysql":
            driver = "mysql+pymysql" if sync else "mysql+aiomysql"
        else:
            raise ValueError(f"Driver '{base_driver}' belum didukung")
        return f"{driver}://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['db']}"

    @cached_property
    def is_production(self):
        return self.APP_ENV == "production"

    @cached_property
    def model_loader(self):
        return ModelLoader(model_path=self.GEMMA_PATH)

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
