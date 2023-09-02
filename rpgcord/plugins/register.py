from typing import Any, List, Optional, Tuple, cast
import disnake
from disnake.ext import plugins
import loguru

from rpgcord.bot import RPGcord
from rpgcord.config import config
from rpgcord.data.custom_ids import CustomId
from rpgcord.data.registration_data import questions
from rpgcord.data.characteristic_data import characteristics
from rpgcord.utils import (
    dump_state, parse_state, check_cid,
    relict, localize as _, mkembed,
)

plugin: plugins.Plugin[RPGcord] = plugins.Plugin(name = "register")


@plugin.global_application_command_check
async def is_registered(inter: disnake.AppCmdInter) -> bool:
    registered = False  # TODO: fetch from db

    if not registered and inter.application_command.name != "register":
        await inter.response.send_message(_("not_registered", inter))
        return False

    return True


@plugin.slash_command()
async def register(inter: disnake.AppCmdInter) -> None:
    await inter.response.send_message(
        embed=mkembed(
            title=_("registration_title", inter),
            description=_("registration_start_desc", inter),
        ),
        components=[
            disnake.ui.Button(
                label=_("registration_start_lets_go", inter),
                style=disnake.ButtonStyle.primary,
                custom_id=CustomId.REGISTRATION_BUTTON_LETS_GO,
            ),
        ],
    )


@plugin.listener("on_button_click")
async def registration_start_handler(inter: disnake.MessageInteraction) -> None:
    if not check_cid(inter.component.custom_id, CustomId.REGISTRATION_BUTTON_LETS_GO):
        return

    await registration_respond_to_answer(inter, -1)


@plugin.listener("on_dropdown")
async def registration_answer_handler(inter: disnake.MessageInteraction) -> None:
    if not check_cid(inter.component.custom_id, CustomId.REGISTRATION_QUESTION):
        return

    await registration_respond_to_answer(inter)


async def registration_respond_to_answer(
    inter: disnake.MessageInteraction,
    previous_index: Optional[int] = None,
) -> None:
    if inter.component.custom_id is None:
        return

    # индекс вопроса, который мы сейчас (в теории) должны спросить
    index = (previous_index or int(parse_state(inter.component.custom_id).idx)) + 1

    if index >= len(questions):
        await registration_initialize_characteristic_manager(inter)
        return

    q_embed, q_select = create_question_message(index, inter)

    await inter.response.edit_message(
        embed=q_embed,
        components=[q_select],
    )

def create_question_message(
    index: int,
    inter: disnake.AppCmdInter | disnake.MessageInteraction,
) -> Tuple[disnake.Embed, disnake.ui.StringSelect[Any]]:
    question = questions[index]

    return (
        mkembed(
            title=_("registration_title", inter),
            description=_(question.l10n_desc, inter),
        ),
        disnake.ui.StringSelect(
            min_values=1,
            max_values=1,
            placeholder=_("registration_select_placeholder", inter),
            options=[
                disnake.SelectOption(
                    label=_(option.l10n_title, inter),
                    description=_(option.l10n_desc, inter),
                )
                for option
                in question.options
            ],
            custom_id=CustomId.REGISTRATION_QUESTION_TEMPLATE.format(index),
        ),
    )


async def registration_initialize_characteristic_manager(
    inter: disnake.MessageInteraction,
) -> None:
    await inter.response.edit_message(
        embed=mkembed(
            title=_("registration_title", inter),
            description=create_charmgr_description(inter, None),
        ),
        components=create_charmgr_components(inter),
    )


@plugin.listener("on_button_click")
async def registration_charmgr_adjust_handler(inter: disnake.MessageInteraction) -> None:
    if not check_cid(inter.component.custom_id, CustomId.REGISTRATION_CHARMGR_ADJUST_CHAR_LEVEL):
        return

    selected_char = get_selected_char(inter)

    if selected_char == "none":
        await inter.response.send_message(
            _("registration_charmgr_adjust_no_char_selected", inter),
            ephemeral=True,
        )
        return

    done_state = get_done_button_state(inter)

    if not done_state.get(selected_char):
        done_state[selected_char] = 0

    match parse_state(inter.component.custom_id).adj:
        case "+":
            done_state[selected_char] = int(done_state[selected_char]) + 1
        case "-":
            done_state[selected_char] = int(done_state[selected_char]) - 1
        case _:
            pass

    await inter.response.edit_message(
        embed=mkembed(
            title=_("registration_title", inter),
            description=create_charmgr_description(inter, done_state),
        ),
        components=create_charmgr_components(inter, done_state),
    )


@plugin.listener("on_dropdown")
async def registration_charmgr_select_char_handler(inter: disnake.MessageInteraction) -> None:
    if not check_cid(inter.component.custom_id, CustomId.REGISTRATION_CHARMGR_SELECT_CHAR):
        return

    if inter.values is None:
        return

    done_state = get_done_button_state(inter)

    await inter.response.edit_message(
        embed=mkembed(
            title=_("registration_title", inter),
            description=create_charmgr_description(inter, done_state),
        ),
        components=create_charmgr_components(inter, done_state, inter.values[0]),
    )


def create_charmgr_description(
    inter: disnake.MessageInteraction,
    done_state: Optional[relict[str, Any]] = None,
) -> str:
    if inter.component.custom_id is None:
        return "Error: custom_id is None"

    state = (
        create_default_characteristic_state()
        if done_state is None
        else done_state
    )

    return "".join((
        _("registration_charmgr_desc", inter) + "\n\n",
        *(
            f"{_(char.l10n_name, inter)}: **{state.get(char.key) or 0}**\n"
            for char
            in characteristics
        ),
    ))


def create_charmgr_components(
    inter: disnake.MessageInteraction,
    done_state: Optional[relict[str, Any]] = None,
    selected_char: Optional[str] = None,
) -> disnake.ui.Components[disnake.ui.MessageUIComponent]:
    if selected_char is None:
        selected_char = get_selected_char(inter)

    return [
        [
            disnake.ui.StringSelect(
                placeholder=_("registration_charmgr_select_placeholder", inter),
                options=[
                    disnake.SelectOption(
                        label=_(char.l10n_name, inter),
                        description=_(char.l10n_desc, inter),
                        value=char.key,
                        default=char.key == selected_char,
                    )
                    for char
                    in characteristics
                ],
                custom_id=CustomId.REGISTRATION_CHARMGR_SELECT_CHAR_TEMPLATE.format(selected_char),
            ),
        ],
        [
            disnake.ui.Button(
                label=_("registration_charmgr_adjust_plus_one", inter),
                style=disnake.ButtonStyle.green,
                custom_id=CustomId.REGISTRATION_CHARMGR_ADJUST_CHAR_LEVEL_TEMPLATE.format("+"),
            ),
            disnake.ui.Button(
                label=_("registration_charmgr_adjust_minus_one", inter),
                style=disnake.ButtonStyle.green,
                custom_id=CustomId.REGISTRATION_CHARMGR_ADJUST_CHAR_LEVEL_TEMPLATE.format("-"),
            ),
            disnake.ui.Button(
                label=_("registration_charmgr_done", inter),
                style=disnake.ButtonStyle.blurple,
                custom_id=(
                    CustomId.REGISTRATION_CHARMGR_DONE
                    if done_state is None
                    else dump_state(CustomId.REGISTRATION_CHARMGR_DONE, done_state)
                ),
            ),
        ],
    ]

# TODO: Deduplicate below two

def get_done_button_state(inter: disnake.MessageInteraction) -> relict[str, Any]:
    for row in inter.message.components:
        for comp in row.children:
            if check_cid(comp.custom_id, CustomId.REGISTRATION_CHARMGR_DONE):
                return parse_state(comp.custom_id)

    loguru.logger.error("done button not found")
    return relict()


def get_selected_char(inter: disnake.MessageInteraction) -> str:
    for row in inter.message.components:
        for comp in row.children:
            if check_cid(comp.custom_id, CustomId.REGISTRATION_CHARMGR_SELECT_CHAR):
                return parse_state(comp.custom_id).char

    loguru.logger.error("chamgr select not found")
    return "none"


def create_default_characteristic_state() -> relict[str, int]:
    return relict({
        char.key: 0
        for char
        in characteristics
    })


@plugin.listener("on_button_click")
async def registration_charmgr_done_handler(inter: disnake.MessageInteraction) -> None:
    if not check_cid(inter.component.custom_id, CustomId.REGISTRATION_CHARMGR_DONE):
        return

    done_state = get_done_button_state(inter)
    recommended_classes = get_recommended_classes(done_state)

    await inter.response.edit_message(
        embed=mkembed(
            title=_("registration_title", inter),
            description=create_choose_a_class_desc(inter),
        ),
        components=create_charmgr_components(inter, done_state),
    )


setup, teardown = plugin.create_extension_handlers()
