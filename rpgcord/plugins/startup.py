from disnake.ext import plugins

from rpgcord.bot import RPGcord

plugin: plugins.Plugin[RPGcord] = plugins.Plugin(name = "startup")


@plugin.listener("on_ready")
async def on_ready() -> None:
    print("Ready to go!")


setup, teardown = plugin.create_extension_handlers()
