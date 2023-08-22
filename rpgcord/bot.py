import aiomysql
from disnake.ext import commands


class RPGcord(commands.InteractionBot):
    """RPGcord."""

    db: aiomysql.Connection
    cursor: aiomysql.Cursor
