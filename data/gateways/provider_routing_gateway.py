from urllib.parse import urlsplit

from data.gateways.gateway_http import normalize_url
from domain.entities.language_model_settings import LanguageModelSettings
from domain.gateways.language_model_gateway import LanguageModelGateway

ANTHROPIC_HOST = "api.anthropic.com"
GEMINI_HOST = "generativelanguage.googleapis.com"
OPENAI_COMPATIBLE_PATH_MARKER = "/chat/completions"


class ProviderRoutingGateway(LanguageModelGateway):
    def __init__(
        self,
        openai_compatible_gateway: LanguageModelGateway,
        anthropic_gateway: LanguageModelGateway,
        gemini_gateway: LanguageModelGateway,
    ):
        self._openai_compatible_gateway = openai_compatible_gateway
        self._anthropic_gateway = anthropic_gateway
        self._gemini_gateway = gemini_gateway

    def ask(self, settings: LanguageModelSettings, question_text: str) -> str:
        return self._select_gateway(settings.endpoint_url).ask(settings, question_text)

    def _select_gateway(self, endpoint_url: str) -> LanguageModelGateway:
        parts = urlsplit(normalize_url(endpoint_url))
        if OPENAI_COMPATIBLE_PATH_MARKER in parts.path:
            return self._openai_compatible_gateway
        if parts.hostname == ANTHROPIC_HOST:
            return self._anthropic_gateway
        if parts.hostname == GEMINI_HOST:
            return self._gemini_gateway
        return self._openai_compatible_gateway
