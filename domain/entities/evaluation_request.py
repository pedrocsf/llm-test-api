from dataclasses import dataclass

from domain.entities.language_model_settings import LanguageModelSettings
from domain.entities.question import Question
from domain.scoring.scoring_method import ScoringMethod


@dataclass(frozen=True)
class EvaluationRequest:
    settings: LanguageModelSettings
    questions: tuple[Question, ...]
    method: ScoringMethod
