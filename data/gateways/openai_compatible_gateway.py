import httpx

from data.gateways.gateway_http import normalize_url, post_json
from domain.entities.language_model_settings import LanguageModelSettings
from domain.errors import LanguageModelError
from domain.gateways.language_model_gateway import LanguageModelGateway

REQUEST_TIMEOUT_SECONDS = 300.0


def _build_headers(settings: LanguageModelSettings) -> dict:
    if not settings.api_key:
        return {}
    return {"Authorization": f"Bearer {settings.api_key}"}


def _build_payload(settings: LanguageModelSettings, question_text: str) -> dict:
    payload = {"messages": [{"role": "user", "content": question_text}]}
    if settings.model_name:
        payload["model"] = settings.model_name
    return payload


class OpenAiCompatibleGateway(LanguageModelGateway):
    def __init__(self, client: httpx.Client | None = None):
        self._client = client or httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS)

    def ask(self, settings: LanguageModelSettings, question_text: str) -> str:
        response = post_json(
            self._client,
            normalize_url(settings.endpoint_url),
            _build_payload(settings, question_text),
            _build_headers(settings),
        )
        return self._extract_answer(response)

    def _extract_answer(self, response: httpx.Response) -> str:
        try:
            return response.json()["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as error:
            raise LanguageModelError(
                "The LLM response is not in the expected format (choices[0].message.content)."
            ) from error
