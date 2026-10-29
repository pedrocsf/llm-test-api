import json

import httpx
import pytest

from data.gateways.anthropic_gateway import AnthropicGateway
from domain.entities.language_model_settings import LanguageModelSettings
from domain.errors import LanguageModelError

ANSWER_BODY = {"content": [{"type": "text", "text": "Brasília"}]}
MESSAGES_URL = "https://api.anthropic.com/v1/messages"


def build_gateway(handler):
    return AnthropicGateway(httpx.Client(transport=httpx.MockTransport(handler)))


def build_settings(**overrides):
    values = {"endpoint_url": MESSAGES_URL, "api_key": "secret", "model_name": "claude-sonnet-4-5"}
    values.update(overrides)
    return LanguageModelSettings(**values)


def test_returns_answer_text():
    gateway = build_gateway(lambda request: httpx.Response(200, json=ANSWER_BODY))

    assert gateway.ask(build_settings(), "Capital?") == "Brasília"


def test_sends_native_headers_and_payload():
    captured = {}

    def handler(request):
        captured["headers"] = request.headers
        captured["payload"] = json.loads(request.content)
        return httpx.Response(200, json=ANSWER_BODY)

    build_gateway(handler).ask(build_settings(), "Capital?")

    assert captured["headers"]["x-api-key"] == "secret"
    assert captured["headers"]["anthropic-version"] == "2023-06-01"
    assert "authorization" not in captured["headers"]
    assert captured["payload"]["model"] == "claude-sonnet-4-5"
    assert captured["payload"]["max_tokens"] > 0
    assert captured["payload"]["messages"] == [{"role": "user", "content": "Capital?"}]


def test_completes_path_and_scheme_when_only_host_is_given():
    captured = {}

    def handler(request):
        captured["url"] = str(request.url)
        return httpx.Response(200, json=ANSWER_BODY)

    build_gateway(handler).ask(build_settings(endpoint_url="api.anthropic.com"), "Capital?")

    assert captured["url"] == MESSAGES_URL


def test_joins_text_blocks_and_skips_other_blocks():
    body = {
        "content": [
            {"type": "thinking", "thinking": "hmm"},
            {"type": "text", "text": "Bra"},
            {"type": "text", "text": "sília"},
        ]
    }
    gateway = build_gateway(lambda request: httpx.Response(200, json=body))

    assert gateway.ask(build_settings(), "Capital?") == "Brasília"


def test_requires_model_name():
    gateway = build_gateway(lambda request: httpx.Response(200, json=ANSWER_BODY))

    with pytest.raises(LanguageModelError, match="Model"):
        gateway.ask(build_settings(model_name=None), "Capital?")


def test_fails_on_error_status():
    gateway = build_gateway(lambda request: httpx.Response(401, text="invalid x-api-key"))

    with pytest.raises(LanguageModelError, match="401"):
        gateway.ask(build_settings(), "Capital?")


def test_fails_on_unexpected_body():
    gateway = build_gateway(lambda request: httpx.Response(200, json={"unexpected": True}))

    with pytest.raises(LanguageModelError, match="expected format"):
        gateway.ask(build_settings(), "Capital?")
