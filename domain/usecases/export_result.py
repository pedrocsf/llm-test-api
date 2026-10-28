from pathlib import Path

from domain.entities.evaluation_result import EvaluationResult
from domain.repositories.result_repository import ResultRepository


class ExportResult:
    def __init__(self, result_repository: ResultRepository):
        self._result_repository = result_repository

    def execute(self, result: EvaluationResult, destination: Path) -> None:
        self._result_repository.save(result, destination)
