from disnake.ext import plugins

plugin = plugins.Plugin(name = "startup")


@plugin.listener("on_ready")
async def on_ready():
    print("Ready to go!")


setup, teardown = plugin.create_extension_handlers()
