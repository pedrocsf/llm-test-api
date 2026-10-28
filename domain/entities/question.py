from dataclasses import dataclass


@dataclass(frozen=True)
class Question:
    identifier: str
    text: str
    expected_answer: str
