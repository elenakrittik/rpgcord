import disnake
import asyncio

from .bot import RPGcord
from .config import config


async def main():
    bot = RPGcord(intents = disnake.Intents.all())
    bot.load_extensions("./rpgcord/plugins")
    bot.i18n.load("./locale")  # type: ignore

    await bot.start(config.token)


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

try:
    loop.run_until_complete(main())
except KeyboardInterrupt:
    pass

loop.close()
