import asyncmy
from .config import config


async def create_tables() -> None:
    con = await asyncmy.connect(host = config.db.connaddr,
                                port = config.db.connport,
                                user = config.db.username,
                                password = config.db.password,
                                db = config.db.database)

    async with con.cursor() as cur:  # type: ignore[reportUnknownVariableType]
        await cur.execute(  # type: ignore[reportUnknownVariableType]
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT,
                name VARCHAR(255)
            );
        """)
        await con.commit()

    con.close()
