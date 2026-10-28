import csv
import json
from pathlib import Path

from domain.entities.evaluation_metrics import EvaluationMetrics
from domain.entities.evaluation_result import EvaluationResult
from domain.entities.question_score import QuestionScore
from domain.errors import ResultExportError
from domain.repositories.result_repository import ResultRepository

JSON_SUFFIX = ".json"
CSV_SUFFIX = ".csv"
CSV_COLUMNS = ("id", "question", "expected_answer", "given_answer", "method", "score", "response_seconds")


def _score_to_row(score: QuestionScore, method_identifier: str) -> dict:
    return {
        "id": score.question.identifier,
        "question": score.question.text,
        "expected_answer": score.question.expected_answer,
        "given_answer": score.given_answer,
        "method": method_identifier,
        "score": score.score,
        "response_seconds": score.response_seconds,
    }


def _metrics_to_dict(metrics: EvaluationMetrics) -> dict:
    return {
        "question_count": metrics.question_count,
        "median_score": metrics.median_score,
        "highest_score": metrics.highest.score,
        "highest_score_question_id": metrics.highest.question.identifier,
        "lowest_score": metrics.lowest.score,
        "lowest_score_question_id": metrics.lowest.question.identifier,
        "correct_count": metrics.correct_count,
        "corpus_score": metrics.corpus_score,
        "average_response_seconds": metrics.average_response_seconds,
        "fastest_response_seconds": metrics.fastest_response_seconds,
        "slowest_response_seconds": metrics.slowest_response_seconds,
        "total_response_seconds": metrics.total_response_seconds,
        "empty_answer_count": metrics.empty_answer_count,
        "average_answer_length": metrics.average_answer_length,
    }


class FileResultRepository(ResultRepository):
    def save(self, result: EvaluationResult, destination: Path) -> None:
        writers = {JSON_SUFFIX: self._write_json, CSV_SUFFIX: self._write_csv}
        writer = writers.get(destination.suffix.lower())
        if writer is None:
            raise ResultExportError(f"Unsupported file format: '{destination.suffix}'. Use .json or .csv.")
        try:
            writer(result, destination)
        except OSError as error:
            raise ResultExportError(f"Could not save the result to {destination}: {error}") from error

    def _write_json(self, result: EvaluationResult, destination: Path) -> None:
        document = {
            "evaluated_at": result.evaluated_at.isoformat(timespec="seconds"),
            "method": result.method.identifier,
            "method_name": result.method.display_name,
            "average_score": result.average_score,
            "metrics": _metrics_to_dict(result.metrics),
            "scores": [_score_to_row(score, result.method.identifier) for score in result.scores],
        }
        destination.write_text(json.dumps(document, ensure_ascii=False, indent=2), encoding="utf-8")

    def _write_csv(self, result: EvaluationResult, destination: Path) -> None:
        with destination.open("w", encoding="utf-8-sig", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            writer.writerows(_score_to_row(score, result.method.identifier) for score in result.scores)
