from abc import ABC, abstractmethod
from pathlib import Path

from domain.entities.evaluation_result import EvaluationResult


class ResultRepository(ABC):
    @abstractmethod
    def save(self, result: EvaluationResult, destination: Path) -> None:
        ...
