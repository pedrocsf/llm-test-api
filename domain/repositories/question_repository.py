from abc import ABC, abstractmethod
from pathlib import Path

from domain.entities.question import Question


class QuestionRepository(ABC):
    @abstractmethod
    def load(self, source: Path) -> list[Question]:
        ...
