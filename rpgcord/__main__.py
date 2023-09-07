import asyncio
import contextlib

import disnake
from disnake.ext.fluent import FluentStore

from .bot import RPGcord
from .config import config


async def main() -> None:
    bot = RPGcord(intents = disnake.Intents.all())
    bot.load_extensions("./rpgcord/plugins")
    bot.i18n = FluentStore(strict=True)
    bot.i18n.load("./locale")

    await bot.start(config.bot.token)


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

with contextlib.suppress(KeyboardInterrupt):
    loop.run_until_complete(main())

loop.close()
