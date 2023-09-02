from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Config:
    db: DatabaseConfig
    token: str  # Bot token ("ihaifbiobiof.faifhhaf.sjebfisbgibgi")


@dataclass
class DatabaseConfig:
    username: str  # MySQL database username ("rpgcord")
    password: str  # MySQL database password ("12345678")
    database: str  # MySQL database database name ("rpgcord")
    connport: int  # MySQL database connection port ("3306")
    connaddr: str  # MySQL database connection address ("127.0.0.1")


config = Config(
    db = DatabaseConfig(
        username = "rpgcord",
        password = "lol198",
        database = "rpgcord",
        connport = 3307,
        connaddr = "127.0.0.1",
    ),
    token = "",
)
