from dataclasses import dataclass
from typing import Self

@dataclass
class Characteristic:
    key: str
    l10n_name: str
    l10n_desc: str

    def __hash__(self: Self) -> int:
        return hash(self.key)


INITIAL_CHARACTERISTIC_COUNT = 10


characteristics = {
    "iq": Characteristic(
        key="iq",
        l10n_name="characteristic_iq_name",
        l10n_desc="characteristic_iq_desc",
    ),
    "force": Characteristic(
        key="force",
        l10n_name="characteristic_force_name",
        l10n_desc="characteristic_force_desc",
    ),
    "agility": Characteristic(
        key="agility",
        l10n_name="characteristic_agility_name",
        l10n_desc="characteristic_agility_desc",
    ),
}
