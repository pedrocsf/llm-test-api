import httpx

from data.gateways.gateway_http import HTTPS_URL_SCHEME, normalize_url, post_json, with_default_path
from domain.entities.language_model_settings import LanguageModelSettings
from domain.errors import LanguageModelError
from domain.gateways.language_model_gateway import LanguageModelGateway

REQUEST_TIMEOUT_SECONDS = 300.0
MESSAGES_PATH = "/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
MAX_OUTPUT_TOKENS = 4096
TEXT_BLOCK_TYPE = "text"
MODEL_REQUIRED_MESSAGE = "Anthropic requires the Model field."


def _build_headers(settings: LanguageModelSettings) -> dict:
    headers = {"anthropic-version": ANTHROPIC_VERSION}
    if settings.api_key:
        headers["x-api-key"] = settings.api_key
    return headers


def _build_payload(settings: LanguageModelSettings, question_text: str) -> dict:
    return {
        "model": settings.model_name,
        "max_tokens": MAX_OUTPUT_TOKENS,
        "messages": [{"role": "user", "content": question_text}],
    }


class AnthropicGateway(LanguageModelGateway):
    def __init__(self, client: httpx.Client | None = None):
        self._client = client or httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS)

    def ask(self, settings: LanguageModelSettings, question_text: str) -> str:
        if not settings.model_name:
            raise LanguageModelError(MODEL_REQUIRED_MESSAGE)
        url = with_default_path(normalize_url(settings.endpoint_url, HTTPS_URL_SCHEME), MESSAGES_PATH)
        response = post_json(
            self._client,
            url,
            _build_payload(settings, question_text),
            _build_headers(settings),
        )
        return self._extract_answer(response)

    def _extract_answer(self, response: httpx.Response) -> str:
        try:
            blocks = response.json()["content"]
            return "".join(block["text"] for block in blocks if block["type"] == TEXT_BLOCK_TYPE)
        except (ValueError, KeyError, TypeError) as error:
            raise LanguageModelError(
                "The LLM response is not in the expected format (content[].text)."
            ) from error
