import json
from pathlib import Path

from domain.entities.question import Question
from domain.errors import QuestionsUnavailableError
from domain.repositories.question_repository import QuestionRepository

QUESTION_KEY = "question"
EXPECTED_ANSWER_KEY = "expected_answer"
IDENTIFIER_KEY = "id"


class JsonQuestionRepository(QuestionRepository):
    def load(self, source: Path) -> list[Question]:
        entries = self._read_entries(source)
        return [self._build_question(position, entry) for position, entry in enumerate(entries, start=1)]

    def _read_entries(self, source: Path) -> list:
        try:
            content = json.loads(source.read_text(encoding="utf-8"))
        except OSError as error:
            raise QuestionsUnavailableError(f"Could not read the questions file {source}: {error}") from error
        except ValueError as error:
            raise QuestionsUnavailableError(f"The questions file {source} is not valid JSON: {error}") from error
        if not isinstance(content, list):
            raise QuestionsUnavailableError("The questions file must contain a list of JSON objects.")
        return content

    def _build_question(self, position: int, entry: object) -> Question:
        if not isinstance(entry, dict):
            raise QuestionsUnavailableError(f"Question {position} must be a JSON object.")
        for required_key in (QUESTION_KEY, EXPECTED_ANSWER_KEY):
            if not isinstance(entry.get(required_key), str) or not entry[required_key].strip():
                raise QuestionsUnavailableError(
                    f"Question {position} is missing the required field '{required_key}'."
                )
        return Question(
            identifier=str(entry.get(IDENTIFIER_KEY, position)),
            text=entry[QUESTION_KEY],
            expected_answer=entry[EXPECTED_ANSWER_KEY],
        )
