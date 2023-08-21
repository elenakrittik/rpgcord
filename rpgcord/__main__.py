import disnake

from .bot import RPGcord
from .config import config

bot = RPGcord(intents = disnake.Intents.all())
bot.load_extensions("./rpgcord/plugins")
bot.i18n.load("./locale")  # type: ignore

bot.run(config.token)
