from dataclasses import dataclass
from os import getenv


@dataclass
class BotConfig:
    token: str = getenv("BOT_TOKEN")
    

@dataclass
class DatabaseConfig:
    database: str = getenv("POSTGRES_DATABASE")
    db_host: str = getenv("POSTGRES_USER")
    db_user: str = getenv("POSTGRES_USER")
    db_password: str = getenv("POSTGRES_PASSWORD")
    dp_port: str = getenv("POSTGRES_PORT")


@dataclass
class RedisConfig:
    host: str = getenv("REDIS_HOST")
    port: int = getenv("REDIS_PORT")


@dataclass
class Configuration:
    bot = BotConfig
    db = DatabaseConfig
    redis = RedisConfig


configuration = Configuration()
