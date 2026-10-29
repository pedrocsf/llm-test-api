import httpx

from data.gateways.gateway_http import HTTPS_URL_SCHEME, normalize_url, post_json, with_default_path
from domain.entities.language_model_settings import LanguageModelSettings
from domain.errors import LanguageModelError
from domain.gateways.language_model_gateway import LanguageModelGateway

REQUEST_TIMEOUT_SECONDS = 300.0
GENERATE_CONTENT_PATH_TEMPLATE = "/v1beta/models/{model_name}:generateContent"
MODEL_REQUIRED_MESSAGE = "Gemini requires the Model field when the URL has no path."


def _build_headers(settings: LanguageModelSettings) -> dict:
    if not settings.api_key:
        return {}
    return {"x-goog-api-key": settings.api_key}


def _build_payload(question_text: str) -> dict:
    return {"contents": [{"role": "user", "parts": [{"text": question_text}]}]}


class GeminiGateway(LanguageModelGateway):
    def __init__(self, client: httpx.Client | None = None):
        self._client = client or httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS)

    def ask(self, settings: LanguageModelSettings, question_text: str) -> str:
        response = post_json(
            self._client,
            self._resolve_url(settings),
            _build_payload(question_text),
            _build_headers(settings),
        )
        return self._extract_answer(response)

    def _resolve_url(self, settings: LanguageModelSettings) -> str:
        url = normalize_url(settings.endpoint_url, HTTPS_URL_SCHEME)
        if not settings.model_name:
            return url
        return with_default_path(url, GENERATE_CONTENT_PATH_TEMPLATE.format(model_name=settings.model_name))

    def _extract_answer(self, response: httpx.Response) -> str:
        try:
            parts = response.json()["candidates"][0]["content"]["parts"]
            return "".join(part.get("text", "") for part in parts)
        except (ValueError, KeyError, IndexError, TypeError, AttributeError) as error:
            raise LanguageModelError(
                "The LLM response is not in the expected format (candidates[0].content.parts[].text)."
            ) from error
