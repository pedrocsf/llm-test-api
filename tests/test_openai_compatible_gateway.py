import json

import httpx
import pytest

from data.gateways.openai_compatible_gateway import OpenAiCompatibleGateway
from domain.entities.language_model_settings import LanguageModelSettings
from domain.errors import LanguageModelError

ANSWER_BODY = {"choices": [{"message": {"content": "Brasília"}}]}


def build_gateway(handler):
    return OpenAiCompatibleGateway(httpx.Client(transport=httpx.MockTransport(handler)))


def test_returns_answer_content():
    gateway = build_gateway(lambda request: httpx.Response(200, json=ANSWER_BODY))

    answer = gateway.ask(LanguageModelSettings("http://127.0.0.1:1234/v1/chat/completions"), "Capital?")

    assert answer == "Brasília"


def test_omits_optional_fields_when_not_given():
    captured = {}

    def handler(request):
        captured["headers"] = request.headers
        captured["payload"] = json.loads(request.content)
        return httpx.Response(200, json=ANSWER_BODY)

    build_gateway(handler).ask(LanguageModelSettings("http://127.0.0.1:1234/v1/chat/completions"), "Capital?")

    assert "authorization" not in captured["headers"]
    assert "model" not in captured["payload"]
    assert captured["payload"]["messages"] == [{"role": "user", "content": "Capital?"}]


def test_sends_api_key_and_model_when_given():
    captured = {}

    def handler(request):
        captured["headers"] = request.headers
        captured["payload"] = json.loads(request.content)
        return httpx.Response(200, json=ANSWER_BODY)

    settings = LanguageModelSettings("http://127.0.0.1:1234/v1/chat/completions", api_key="secret", model_name="llama")
    build_gateway(handler).ask(settings, "Capital?")

    assert captured["headers"]["authorization"] == "Bearer secret"
    assert captured["payload"]["model"] == "llama"


def test_prepends_http_scheme_when_missing():
    captured = {}

    def handler(request):
        captured["url"] = str(request.url)
        return httpx.Response(200, json=ANSWER_BODY)

    build_gateway(handler).ask(LanguageModelSettings("127.0.0.1:1234/v1/chat/completions"), "Capital?")

    assert captured["url"] == "http://127.0.0.1:1234/v1/chat/completions"


def test_fails_on_error_status():
    gateway = build_gateway(lambda request: httpx.Response(500, text="boom"))

    with pytest.raises(LanguageModelError, match="500"):
        gateway.ask(LanguageModelSettings("http://127.0.0.1:1234/v1/chat/completions"), "Capital?")


def test_fails_on_unexpected_body():
    gateway = build_gateway(lambda request: httpx.Response(200, json={"unexpected": True}))

    with pytest.raises(LanguageModelError, match="expected format"):
        gateway.ask(LanguageModelSettings("http://127.0.0.1:1234/v1/chat/completions"), "Capital?")


def test_fails_when_connection_is_refused():
    def handler(request):
        raise httpx.ConnectError("refused")

    with pytest.raises(LanguageModelError, match="Failed to connect"):
        build_gateway(handler).ask(LanguageModelSettings("http://127.0.0.1:1234/v1/chat/completions"), "Capital?")
