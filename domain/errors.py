class DomainError(Exception):
    pass


class LanguageModelError(DomainError):
    pass


class QuestionsUnavailableError(DomainError):
    pass


class ModelUnavailableError(DomainError):
    pass


class EvaluationCancelledError(DomainError):
    pass


class ResultExportError(DomainError):
    pass
