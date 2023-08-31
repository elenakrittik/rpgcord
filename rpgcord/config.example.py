from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

import disnake

__all__: tuple[str, ...] = (
    "Environment",
    "config",
)


@dataclass
class Config:
    db: DatabaseConfig
    colors: ColorConfig
    bot: BotConfig


@dataclass
class DatabaseConfig:
    username: str  # MySQL database username ("rpgcord")
    password: str  # MySQL database password ("12345678")
    database: str  # MySQL database database name ("rpgcord")
    connport: int  # MySQL database connection port ("3306")
    connaddr: str  # MySQL database connection address ("127.0.0.1")


@dataclass
class ColorConfig:
    primary_color: disnake.Color

@dataclass
class BotConfig:
    token: str  # Bot token ("ihaifbiobiof.faifhhaf.sjebfisbgibgi")
    environment: Environment

class Environment(Enum):
    Production = 0
    Debug = 1
    Development = 2


config = Config(
    db = DatabaseConfig(
        username = "rpgcord",
        password = "mypassword",
        database = "rpgcord",
        connport = 3306,
        connaddr = "127.0.0.1",
    ),
    colors = ColorConfig(
        primary_color = disnake.Color.fuchsia(),
    ),
    bot = BotConfig(
        token = "",
        environment = Environment.Debug,
    ),
)
