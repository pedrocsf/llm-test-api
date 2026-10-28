import json

import pytest

from data.repositories.json_question_repository import JsonQuestionRepository
from domain.errors import QuestionsUnavailableError


def write_questions(tmp_path, content):
    path = tmp_path / "questions.json"
    path.write_text(json.dumps(content), encoding="utf-8")
    return path


def test_reads_questions_with_and_without_identifier(tmp_path):
    path = write_questions(
        tmp_path,
        [
            {"id": "abc", "question": "q1?", "expected_answer": "a1"},
            {"question": "q2?", "expected_answer": "a2"},
        ],
    )

    questions = JsonQuestionRepository().load(path)

    assert [(q.identifier, q.text, q.expected_answer) for q in questions] == [
        ("abc", "q1?", "a1"),
        ("2", "q2?", "a2"),
    ]


def test_rejects_missing_file(tmp_path):
    with pytest.raises(QuestionsUnavailableError):
        JsonQuestionRepository().load(tmp_path / "missing.json")


def test_rejects_invalid_json(tmp_path):
    path = tmp_path / "questions.json"
    path.write_text("{not json", encoding="utf-8")

    with pytest.raises(QuestionsUnavailableError, match="not valid JSON"):
        JsonQuestionRepository().load(path)


def test_rejects_file_that_is_not_utf8_text(tmp_path):
    path = tmp_path / "questions.json"
    path.write_bytes(b"\xff\xfe\x00binary")

    with pytest.raises(QuestionsUnavailableError, match="not valid JSON"):
        JsonQuestionRepository().load(path)


def test_rejects_non_list_root(tmp_path):
    with pytest.raises(QuestionsUnavailableError):
        JsonQuestionRepository().load(write_questions(tmp_path, {"question": "x"}))


def test_rejects_entry_without_expected_answer(tmp_path):
    path = write_questions(tmp_path, [{"question": "q?"}])

    with pytest.raises(QuestionsUnavailableError, match="expected_answer"):
        JsonQuestionRepository().load(path)
