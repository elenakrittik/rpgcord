from typing import Any, Optional, Tuple, cast

import disnake
from disnake.ext import plugins

from rpgcord.bot import RPGcord
from rpgcord.data.class_data import NUMBER_OF_RECOMMENDED_CLASSES, classes
from rpgcord.data.custom_ids import CustomId
from rpgcord.data.registration_data import questions
from rpgcord.data.characteristic_data import characteristics
from rpgcord.data.class_data import CharacterClass, temp_dot_values # TODO
from rpgcord.maths import product_of_char_list
from rpgcord.utils import (
    dump_state, parse_state, check_cid,
    relict, localize as _, mkembed,
)
from rpgcord.utils import find_component_by_custom_id

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
        create_chars_outline(inter, state),
    ))


def create_chars_outline(inter: disnake.MessageInteraction, state: relict[str, Any]) -> str:
    return "".join((
        f"{_(char.l10n_name, inter)}: **{state.get(char.key) or 0}**\n"
        for char
        in characteristics.values()
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
                    in characteristics.values()
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

def get_done_button_state(inter: disnake.MessageInteraction) -> relict[str, Any]:
    comp = find_component_by_custom_id(
        inter,
        CustomId.REGISTRATION_CHARMGR_DONE,
        "done button not found",
    )

    if comp and comp.custom_id:
        return parse_state(comp.custom_id)

    return relict()


def get_selected_char(inter: disnake.MessageInteraction) -> str:
    comp = find_component_by_custom_id(
        inter,
        CustomId.REGISTRATION_CHARMGR_SELECT_CHAR,
        "chamgr select not found",
    )

    if comp and comp.custom_id:
        return parse_state(comp.custom_id).char

    return "none"


def create_default_characteristic_state() -> relict[str, int]:
    return relict({
        char.key: 0
        for char
        in characteristics.values()
    })


@plugin.listener("on_button_click")
async def registration_charmgr_done_handler(inter: disnake.MessageInteraction) -> None:
    if not check_cid(inter.component.custom_id, CustomId.REGISTRATION_CHARMGR_DONE):
        return

    done_state = get_done_button_state(inter)
    recommended_classes = await get_recommended_classes(done_state)

    await inter.response.edit_message(
        embed=mkembed(
            title=_("registration_title", inter),
            description=create_choose_a_class_desc(
                inter,
                recommended_classes[0],
            ),
        ),
        components=create_choose_a_class_components(
            inter,
            recommended_classes,
            recommended_classes[0],
            done_state,
        ),
    )


async def get_recommended_classes(done_state: relict[str, Any]) -> list[int]:
    temp = [(key, int(value)) for key, value in done_state.items()] # TODO: there will be a bug when we implement questions
    temp.sort(key=lambda x: ord(x[0][0]))
    chars = [x[1] for x in temp]
    product = product_of_char_list(chars)

    differences: relict[float, CharacterClass] = relict()

    for dot, cls in temp_dot_values.items():
        differences[abs(dot - product)] = cls

    recommended_classes: list[CharacterClass] = []

    while True:
        dot = min(differences.keys())
        recommended_classes.append(differences.pop(dot))

        if len(recommended_classes) >= NUMBER_OF_RECOMMENDED_CLASSES:
            break

    return [classes.index(cls) for cls in recommended_classes]


def create_choose_a_class_desc(
    inter: disnake.MessageInteraction,
    recommended_class: int,
) -> str:
    cls = classes[recommended_class]

    return "".join((
        _("registration_choose_your_class", inter) + "\n\n",
        "**" + _(cls.l10n_title, inter) + "**\n",
        _(cls.l10n_desc, inter),
    ))


def create_choose_a_class_components(
    inter: disnake.MessageInteraction,
    recommended_classes: list[int],
    recommended_class: int,
    done_state: relict[str, Any],
) -> disnake.ui.Components[disnake.ui.MessageUIComponent]:
    return [
        [
            disnake.ui.StringSelect(
                options=[
                    disnake.SelectOption(
                        label=_(classes[cls].l10n_title, inter),
                        value=str(cls),
                        default=cls == recommended_class,
                    )
                    for cls
                    in recommended_classes
                ],
                custom_id=CustomId.REGISTRATION_CHOOSE_A_CLASS_SELECT_TEMPLATE.format(
                    str(recommended_class),
                ),
            ),
        ],
        [
            disnake.ui.Button(
                label=_("registration_choose_your_class_pick_it", inter),
                style=disnake.ButtonStyle.blurple,
                custom_id=dump_state(CustomId.REGISTRATION_CHOOSE_A_CLASS_PICK_IT, done_state),
            ),
        ],
    ]


@plugin.listener("on_dropdown")
async def registration_choose_a_class_select_handler(
    inter: disnake.MessageInteraction,
) -> None:
    if not check_cid(inter.component.custom_id, CustomId.REGISTRATION_CHOOSE_A_CLASS_SELECT):
        return

    state = parse_state(inter.component.custom_id)

    if not inter.values:
        return

    state.cls = int(inter.values[0])

    recommended_classes = [
        int(option.value)
        for option
        in cast(disnake.StringSelectMenu, inter.component).options
    ]

    pick_it_button = find_component_by_custom_id(inter, CustomId.REGISTRATION_CHOOSE_A_CLASS_PICK_IT)

    if not pick_it_button or not pick_it_button.custom_id:
        return

    pick_it_state = parse_state(pick_it_button.custom_id)

    await inter.response.edit_message(
        embed=mkembed(
            title=_("registration_title", inter),
            description=create_choose_a_class_desc(inter, state.cls),
        ),
        components=create_choose_a_class_components(
            inter, recommended_classes,
            state.cls, pick_it_state,
        ),
    )


@plugin.listener("on_button_click")
async def registration_choose_a_class_pick_it_handler(inter: disnake.MessageInteraction) -> None:
    if not check_cid(inter.component.custom_id, CustomId.REGISTRATION_CHOOSE_A_CLASS_PICK_IT):
        return

    cls_select = find_component_by_custom_id(inter, CustomId.REGISTRATION_CHOOSE_A_CLASS_SELECT)

    if not cls_select or not cls_select.custom_id:
        return

    cls_title_key = classes[int(parse_state(cls_select.custom_id).cls)].l10n_title

    char_state = parse_state(inter.component.custom_id)
    char_outline = create_chars_outline(inter, char_state)

    await inter.response.edit_message(
        embed=mkembed(
            title=_("registration_title", inter),
            description="".join((
                _("registration_end_header", inter) + "\n\n",
                "**" + _(cls_title_key, inter) + "**\n\n",
                char_outline,
                "\n\n" + _("registration_end_happy_game", inter),
            )),
        ),
        components=[],
    )


setup, teardown = plugin.create_extension_handlers()

# TODO: простое нажатие готов ломает все
# TODO: можно ставить отрицательные значения
# TODO: можно ставить бесконечно
# TODO: задокументировать
# TODO: локализации команд
# TODO: картинки для классов
# TODO: любая кар-ка 0 ломает реки
# TODO: заставить распределить все очки
# TODO: логи
