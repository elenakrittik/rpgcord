from typing import Any, Self, TypeGuard, TypeVar, cast

import disnake

from rpgcord.bot import RPGcord
from rpgcord.config import config

K = TypeVar("K")
V = TypeVar("V")


class relict(dict[K, V]):
    """Имплементация словаря, позволяющая использовать `x.y` вместо `x["y"]`."""

    def __getattr__(self: Self, attr: str) -> V:
        if attr in dir(self):
            return self.__getattribute__(attr)
        return self[cast(K, attr)]

    def __setattr__(self: Self, attr: str, value: V) -> None:
        if attr in dir(self):
            # __setattribute__ неизвестный член типа
            return self.__setattribute__(attr)  # type: ignore[reportUnknownVariableType]
        self[cast(K, attr)] = value


# no ninjas here
def parse_state(input_: str) -> relict[str, Any]:
    if "=" not in input_:
        return relict()

    input_ = input_[5:].strip() # убираем айди компонента и первый пробел после него
    state: relict[str, Any] = relict() # создаем новый словарь (или реликт, как в нашем случае)

    for param in input_.split(" "):  # param: "abc=123"
        key, value = param.split("=")  # key: "abc"; value: "123"

        state[key] = value

    return state


def dump_state(cid: str, state: relict[str, Any]) -> str:
    return f"{cid} {' '.join(key + '=' + str(value) for key, value in state.items())}"


def check_cid(cid: str | None, expected: str) -> TypeGuard[str]:
    return cid is not None and cid.startswith(expected)


def localize(
    key: str,
    inter: disnake.AppCmdInter | disnake.MessageInteraction,
    **kwargs: Any,  # noqa: ANN401
) -> str:
    """Отвечает за логику определеня языка."""
    locale = inter.guild.preferred_locale if inter.guild else inter.locale
    return cast(RPGcord, inter.bot).i18n.l10n(
        key,
        locale,
        { **kwargs },
    ) or "Localization not found. Sorry."

def mkembed(
    title: str | None,
    description: str | None,
    color: disnake.Color = config.colors.primary_color,
    **kwargs: Any,  # noqa: ANN401
) -> disnake.Embed:
    return disnake.Embed(
        title=title or "Title not found",
        description=description or "Description not found",
        color=color,
        **kwargs,
    )
