import aiomysql
from disnake.ext import commands


class RPGcord(commands.InteractionBot):
    db: aiomysql.Connection
    cursor: aiomysql.Cursor
