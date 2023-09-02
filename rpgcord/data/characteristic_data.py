from dataclasses import dataclass

@dataclass
class Characteristic:
    key: str
    l10n_name: str
    l10n_desc: str


characteristics = [
    Characteristic(
        key="iq",
        l10n_name="characteristic_iq_name",
        l10n_desc="characteristic_iq_desc",
    ),
]
