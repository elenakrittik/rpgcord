from __future__ import annotations

from typing import List
from dataclasses import dataclass


@dataclass
class Question:
    l10n_desc: str  # ключ локализации описания вопроса
    options: List[QuestionOption]


@dataclass
class QuestionOption:
    value: str
    l10n_title: str
    l10n_desc: str


questions: List[Question] = [
    Question(
        l10n_desc="registration_q1_desc",
        options=[
            QuestionOption(
                value="stealth",
                l10n_title="registration_q1o1_title",
                l10n_desc="registration_q1o1_desc",
            ),
        ],
    ),
    Question(
        l10n_desc="registration_q2_desc",
        options=[
            QuestionOption(
                value="abcdc",
                l10n_title="registration_q2o1_title",
                l10n_desc="registration_q2o1_desc",
            ),
        ],
    ),
]
