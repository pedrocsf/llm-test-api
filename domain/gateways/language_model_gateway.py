from abc import ABC, abstractmethod

from domain.entities.language_model_settings import LanguageModelSettings


class LanguageModelGateway(ABC):
    @abstractmethod
    def ask(self, settings: LanguageModelSettings, question_text: str) -> str:
        ...
