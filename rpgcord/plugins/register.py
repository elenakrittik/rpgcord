import disnake
from disnake.ext import plugins

from rpgcord.config import config

plugin = plugins.Plugin(name = "register")


@plugin.global_application_command_check
async def is_registered(inter: disnake.AppCmdInter) -> bool:
    registered = False  # TODO: fetch from db

    if not registered:
        await registration_step_1(inter)
        return False

    return True


async def registration_step_1(inter: disnake.AppCmdInter) -> None:
    embed = disnake.Embed(
        title = "Регистрация",
        description = ("Вы еще не имеете персонажа в мире RPGcord. Давайте создадим!\n"
                       "Отвечайте на появляющиеся вопросы.\n\n"
                       "**Какой ваш любимый стиль игры?**"),
        color = config.colors.primary_color,
    )

    components = [
        disnake.ui.StringSelect(
            max_values = 1,
            custom_id = "0001",
            placeholder = "Выберите ответ",
            options = [
                disnake.SelectOption(
                    label = "Стелс",
                    value = "stealth",
                    description = "Вам нравится сосать хуи",
                ),
            ],
        ),
    ]

    await inter.response.send_message(embed = embed, components = components)


@plugin.listener("on_dropdown")
async def registration_step_2(inter: disnake.MessageInteraction) -> None:
    if inter.component.custom_id != "0001":
        return

    embed = disnake.Embed(
        title = "Регистрация",
        description = ("**Какая поза вам прельщает?**"),
        color = config.colors.primary_color,
    )

    components = [
        disnake.ui.StringSelect(
            max_values = 1,
            custom_id = "0002",
            placeholder = "Выберите ответ",
            options = [
                disnake.SelectOption(
                    label = "Стелс",
                    value = "stealth",
                    description = "Наездница",
                ),
            ],
        ),
    ]

    await inter.response.send_message(embed = embed, components = components)


@plugin.slash_command()
async def test_command(inter: disnake.AppCmdInter) -> None:
    await inter.response.send_message("привет")


setup, teardown = plugin.create_extension_handlers()
