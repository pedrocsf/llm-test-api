import pytest

from data.gateways.provider_routing_gateway import ProviderRoutingGateway
from domain.entities.language_model_settings import LanguageModelSettings
from domain.gateways.language_model_gateway import LanguageModelGateway


class NamedGateway(LanguageModelGateway):
    def __init__(self, name):
        self._name = name

    def ask(self, settings, question_text):
        return self._name


def ask_through_router(endpoint_url):
    router = ProviderRoutingGateway(NamedGateway("openai"), NamedGateway("anthropic"), NamedGateway("gemini"))
    return router.ask(LanguageModelSettings(endpoint_url), "Capital?")


@pytest.mark.parametrize(
    ("endpoint_url", "expected_gateway"),
    [
        ("http://127.0.0.1:1234/v1/chat/completions", "openai"),
        ("https://api.openai.com/v1/chat/completions", "openai"),
        ("https://api.anthropic.com/v1/messages", "anthropic"),
        ("api.anthropic.com", "anthropic"),
        ("https://api.anthropic.com/v1/chat/completions", "openai"),
        ("https://generativelanguage.googleapis.com", "gemini"),
        ("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent", "gemini"),
        ("https://generativelanguage.googleapis.com/v1beta/openai/chat/completions", "openai"),
    ],
)
def test_selects_gateway_by_endpoint(endpoint_url, expected_gateway):
    assert ask_through_router(endpoint_url) == expected_gateway
