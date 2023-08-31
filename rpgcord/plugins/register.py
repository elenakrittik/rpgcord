from typing import Any, cast
import disnake
from disnake.ext import plugins
import loguru

from rpgcord.bot import RPGcord
from rpgcord.config import config
from rpgcord.utils import dump_state, parse_state, check_cid, relict, localize as _

plugin: plugins.Plugin[RPGcord] = plugins.Plugin(name = "register")


@plugin.global_application_command_check
async def is_registered(inter: disnake.AppCmdInter) -> bool:
    registered = False  # TODO: fetch from db

    if not registered:
        await registration_step_1(inter)
        return False

    return True


@plugin.listener("on_dropdown")
async def registration_answer_handler(inter: disnake.MessageInteraction) -> None:



async def registration_step_1(inter: disnake.AppCmdInter) -> None:
    embed = disnake.Embed(
        title = _("registration_title", inter),
        description = _("registration_description_1", inter),
        color = config.colors.primary_color,
    )

    components = [
        disnake.ui.StringSelect(
            max_values = 1,
            min_values = 1,
            custom_id = "0001",
            placeholder = _("registration_select_placeholder", inter),
            options = [
                disnake.SelectOption(
                    label = "Стелс",
                    value = "stealth",
                    description = (
                        "Вам нравится добиваться целей скрытно, "
                        "не привлекая к своей фигуре лишнего внимания"
                    ),
                ),
                disnake.SelectOption(
                    label = "Воин",
                    value = "warrior",
                    description = (
                        "Вам нравится идти напролом, снося все "
                        "преграды на своем пути."
                    ),
                ),
            ],
        ),
    ]

    await inter.response.send_message(embed = embed, components = components)


@plugin.listener("on_dropdown")
async def registration_step_2(inter: disnake.MessageInteraction) -> None:
    if not check_cid(inter.component.custom_id, "0001"):
        return

    embed = disnake.Embed(
        title = "Регистрация",
        description = ("**Если вы ранее играли в другие (MMO)РПГ, какой класс вы предпочитали?**"),
        color = config.colors.primary_color,
    )

    a1 = cast(list[str], inter.values)[0] # ответ на первый вопрос

    components = [
        disnake.ui.StringSelect(
            max_values = 1,
            min_values = 1,
            custom_id = f"0002 a1={a1}",
            placeholder = "Выберите ответ",
            options = [
                disnake.SelectOption(
                    label = "Mage",
                    value = "mage",
                    description = "Пока что тут нет описания.",
                ),
            ],
        ),
    ]

    await inter.response.edit_message(embed = embed, components = components)


@plugin.listener("on_dropdown")
async def registration_step_3(inter: disnake.MessageInteraction) -> None:
    if not check_cid(inter.component.custom_id, "0002"):
        return

    embed = disnake.Embed(
        title = "Регистрация",
        description = ("**Я пока еще не придумал, какой здесь будет вопрос.**"),
        color = config.colors.primary_color,
    )

    a1 = parse_state(inter.component.custom_id).a1
    a2 = cast(list[str], inter.values)[0] # ответ на второй вопрос

    components = [
        disnake.ui.StringSelect(
            max_values = 1,
            min_values = 1,
            custom_id = f"0003 a1={a1} a2={a2}",
            placeholder = "Выберите ответ",
            options = [
                disnake.SelectOption(
                    label = "Плейсхолдер.",
                    value = "placeholder",
                    description = "Плейсхолдер, что тут сказать.",
                ),
            ],
        ),
    ]

    await inter.response.edit_message(embed = embed, components = components)


characteristics_embed_description = (
    "Распределите начальные очки характеристик. (сейчас доступно: {left})\n\n"
    "Сила: **{force}**\n"
    "Интеллект: **{iq}**\n"
)


@plugin.listener("on_dropdown")
async def registration_step_final(inter: disnake.MessageInteraction) -> None:
    if not check_cid(inter.component.custom_id, "0003"):
        return

    state = parse_state(inter.component.custom_id)

    a1 = state.a1
    a2 = state.a2
    a3 = cast(list[str], inter.values)[0] # ответ на третий вопрос

    answers = [a1, a2, a3]

    embed = disnake.Embed(
        title="Регистрация",
        description=characteristics_embed_description.format(force=0, iq=0, left=10),
        color=config.colors.primary_color,
    )

    components = [
        [
            disnake.ui.Button(
                style=disnake.ButtonStyle.green,
                label="+1 к силе",
                custom_id="0004 field=force",
            ),
            disnake.ui.Button(
                style=disnake.ButtonStyle.green,
                label="+1 к интеллекту",
                custom_id="0004 field=iq",
            ),
        ],
        [
            disnake.ui.Button(
                style=disnake.ButtonStyle.blurple,
                label="Готово",
                custom_id=f"0005 answers={','.join(answers)} left=10 force=0 iq=0",
            ),
        ],
    ]

    await inter.response.edit_message(embed = embed, components=components)


@plugin.listener("on_button_click")
async def handle_plus_1_to_characteristic(inter: disnake.MessageInteraction) -> None:
    if not check_cid(inter.component.custom_id, "0004"):
        return

    field = parse_state(inter.component.custom_id).field
    state: relict[str, Any] | None = None

    for comp in inter.message.components[1].children:
        if check_cid(comp.custom_id, "0005"):
            state = parse_state(comp.custom_id)

    if not state:
        loguru.logger.error("Unable to find stateful button while proccessing +1 click.")
        await inter.response.edit_message(
            embed=disnake.Embed(
                title="Упс!",
                description="Что-то пошло не так :<",
            ),
        )
        return

    if int(state.left) > 0:
        state.left = int(state.left) - 1
        state[field] = int(state[field]) + 1

        embed = disnake.Embed(
            title="Регистрация",
            description=characteristics_embed_description.format(
                force=int(state.force),
                iq=int(state.iq),
                left=int(state.left),
            ),
            color=config.colors.primary_color,
        )

        components = [
            [
                disnake.ui.Button(
                    style=disnake.ButtonStyle.green,
                    label="+1 к силе",
                    custom_id="0004 field=force",
                ),
                disnake.ui.Button(
                    style=disnake.ButtonStyle.green,
                    label="+1 к интеллекту",
                    custom_id="0004 field=iq",
                ),
            ],
            [
                disnake.ui.Button(
                    style=disnake.ButtonStyle.blurple,
                    label="Готово",
                    custom_id=dump_state("0005", state),
                ),
            ],
        ]

        await inter.response.edit_message(embed = embed, components=components)

    else:
        await inter.response.send_message("У вас закончились начальные очки.")


@plugin.slash_command()
async def test_command(inter: disnake.AppCmdInter) -> None:
    await inter.response.send_message("привет")


setup, teardown = plugin.create_extension_handlers()
