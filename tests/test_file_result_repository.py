import csv
import json
from datetime import datetime

import pytest

from data.repositories.file_result_repository import FileResultRepository
from domain.entities.evaluation_result import EvaluationResult
from domain.entities.question import Question
from domain.entities.question_score import QuestionScore
from domain.errors import ResultExportError
from domain.scoring.token_f1_scoring_method import TokenF1ScoringMethod


@pytest.fixture
def result():
    scores = (
        QuestionScore(Question("1", "Capital?", "Brasília"), "Brasília, claro", 0.9, 1.5),
        QuestionScore(Question("2", "Autor?", "Machado"), "Não sei", 0.1, 0.5),
    )
    return EvaluationResult(scores, datetime(2026, 10, 28, 12, 0, 0), TokenF1ScoringMethod())


def test_writes_json(tmp_path, result):
    destination = tmp_path / "out.json"

    FileResultRepository().save(result, destination)

    document = json.loads(destination.read_text(encoding="utf-8"))
    assert document["method"] == "token_f1"
    assert document["method_name"] == "Token F1"
    assert document["average_score"] == pytest.approx(0.5)
    assert document["evaluated_at"] == "2026-10-28T12:00:00"
    assert document["scores"][0]["given_answer"] == "Brasília, claro"
    assert document["scores"][0]["score"] == 0.9
    assert document["scores"][0]["response_seconds"] == 1.5
    assert document["metrics"]["highest_score_question_id"] == "1"
    assert document["metrics"]["lowest_score_question_id"] == "2"
    assert document["metrics"]["corpus_score"] is None
    assert document["metrics"]["average_response_seconds"] == pytest.approx(1.0)


def test_writes_csv_readable_with_accents(tmp_path, result):
    destination = tmp_path / "out.csv"

    FileResultRepository().save(result, destination)

    with destination.open(encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))
    assert [row["expected_answer"] for row in rows] == ["Brasília", "Machado"]
    assert [row["method"] for row in rows] == ["token_f1", "token_f1"]
    assert rows[1]["score"] == "0.1"
    assert rows[1]["response_seconds"] == "0.5"


def test_rejects_unsupported_suffix(tmp_path, result):
    with pytest.raises(ResultExportError, match="Unsupported file format"):
        FileResultRepository().save(result, tmp_path / "out.txt")


def test_reports_unwritable_destination(tmp_path, result):
    with pytest.raises(ResultExportError):
        FileResultRepository().save(result, tmp_path / "missing" / "out.json")
