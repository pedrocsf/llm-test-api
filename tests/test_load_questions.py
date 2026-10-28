from pathlib import Path

import pytest

from domain.entities.question import Question
from domain.errors import QuestionsUnavailableError
from domain.repositories.question_repository import QuestionRepository
from domain.usecases.load_questions import LoadQuestions


class FakeQuestionRepository(QuestionRepository):
    def __init__(self, questions):
        self._questions = questions
        self.received_source = None

    def load(self, source):
        self.received_source = source
        return self._questions


def test_returns_questions_from_the_given_source():
    repository = FakeQuestionRepository([Question("1", "a?", "A")])

    questions = LoadQuestions(repository).execute(Path("/data/questions.json"))

    assert [question.identifier for question in questions] == ["1"]
    assert repository.received_source == Path("/data/questions.json")


def test_rejects_a_source_without_questions():
    with pytest.raises(QuestionsUnavailableError, match="questions.json"):
        LoadQuestions(FakeQuestionRepository([])).execute(Path("/data/questions.json"))
