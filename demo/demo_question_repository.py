from collections.abc import Sequence
from pathlib import Path

from demo.demo_data import DemoEntry
from domain.entities.question import Question
from domain.repositories.question_repository import QuestionRepository


class DemoQuestionRepository(QuestionRepository):
    def __init__(self, entries: Sequence[DemoEntry]):
        self._entries = entries

    def load(self, source: Path) -> list[Question]:
        return [Question(entry.identifier, entry.question, entry.expected_answer) for entry in self._entries]
