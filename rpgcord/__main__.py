import disnake
import asyncio

from .bot import RPGcord
from .config import config
import contextlib
from .database import create_base_table


async def main() -> None:
    await create_base_table()

    bot = RPGcord(intents = disnake.Intents.all())
    bot.load_extensions("./rpgcord/plugins")
    bot.i18n.load("./locale")  # type: ignore[reportUnknownMemberType]

    await bot.start(config.token)


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

with contextlib.suppress(KeyboardInterrupt):
    loop.run_until_complete(main())

loop.close()
