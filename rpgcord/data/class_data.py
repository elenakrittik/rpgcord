from dataclasses import dataclass
from typing import List

@dataclass
class CharacterClass:
    key: str
    l10n_title: str


classes: List[CharacterClass] = [
    CharacterClass(
        key="warrior",
        l10n_title="class_warrior_title",
    ),
]
