from pathlib import Path

from domain.entities.question import Question
from domain.errors import QuestionsUnavailableError
from domain.repositories.question_repository import QuestionRepository


class LoadQuestions:
    def __init__(self, question_repository: QuestionRepository):
        self._question_repository = question_repository

    def execute(self, source: Path) -> list[Question]:
        questions = self._question_repository.load(source)
        if not questions:
            raise QuestionsUnavailableError(f"No questions found in {source.name}.")
        return questions
