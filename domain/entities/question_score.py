from dataclasses import dataclass

from domain.entities.question import Question


@dataclass(frozen=True)
class QuestionScore:
    question: Question
    given_answer: str
    score: float
    response_seconds: float
