import httpx

from domain.entities.language_model_settings import LanguageModelSettings
from domain.errors import LanguageModelError
from domain.gateways.language_model_gateway import LanguageModelGateway

REQUEST_TIMEOUT_SECONDS = 300.0
ERROR_BODY_PREVIEW_LENGTH = 300
DEFAULT_URL_SCHEME = "http://"


def _normalize_url(endpoint_url: str) -> str:
    cleaned_url = endpoint_url.strip()
    if "://" in cleaned_url:
        return cleaned_url
    return DEFAULT_URL_SCHEME + cleaned_url


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
        response = self._post(settings, question_text)
        return self._extract_answer(response)

    def _post(self, settings: LanguageModelSettings, question_text: str) -> httpx.Response:
        url = _normalize_url(settings.endpoint_url)
        try:
            response = self._client.post(
                url,
                json=_build_payload(settings, question_text),
                headers=_build_headers(settings),
            )
        except httpx.HTTPError as error:
            raise LanguageModelError(f"Failed to connect to {url}: {error}") from error
        if response.is_error:
            preview = response.text[:ERROR_BODY_PREVIEW_LENGTH]
            raise LanguageModelError(f"The LLM responded with status {response.status_code}: {preview}")
        return response

    def _extract_answer(self, response: httpx.Response) -> str:
        try:
            return response.json()["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as error:
            raise LanguageModelError(
                "The LLM response is not in the expected format (choices[0].message.content)."
            ) from error
