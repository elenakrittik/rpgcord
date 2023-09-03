from dataclasses import dataclass
from typing import List

from rpgcord.maths import product_of_char_list
from rpgcord.utils import relict
from rpgcord.data.characteristic_data import Characteristic, characteristics


@dataclass
class CharacterClass:
    key: str
    l10n_title: str
    l10n_desc: str
    recommended_characteristics: relict[Characteristic, int]


NUMBER_OF_RECOMMENDED_CLASSES = 3


classes: List[CharacterClass] = [
    CharacterClass(
        key="warrior",
        l10n_title="class_warrior_title",
        l10n_desc="class_warrior_desc",
        recommended_characteristics=relict({
            characteristics["iq"]: 2,
            characteristics["force"]: 8,
            characteristics["agility"]: 1,
        }),
    ),
    CharacterClass(
        key="mage",
        l10n_title="class_mage_title",
        l10n_desc="class_mage_desc",
        recommended_characteristics=relict({
            characteristics["iq"]: 10,
            characteristics["force"]: 0,
            characteristics["agility"]: 1,
        }),
    ),
    CharacterClass(
        key="archer",
        l10n_title="class_archer_title",
        l10n_desc="class_archer_desc",
        recommended_characteristics=relict({
            characteristics["iq"]: 5,
            characteristics["force"]: 5,
            characteristics["agility"]: 1,
        }),
    ),
    CharacterClass(
        key="barbarian",
        l10n_title="class_barbarian_title",
        l10n_desc="class_barbarian_desc",
        recommended_characteristics=relict({
            characteristics["iq"]: 1,
            characteristics["force"]: 9,
            characteristics["agility"]: 1,
        }),
    ),
]

temp_dot_values: relict[float, CharacterClass] = relict()

for cls in classes:
    temp = [(key, value) for key, value in cls.recommended_characteristics.items()]
    temp.sort(key=lambda x: ord(x[0].key[0]))
    chars = [x[1] for x in temp]
    temp_dot_values[product_of_char_list(chars)] = cls
