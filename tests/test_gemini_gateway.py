import json

import httpx
import pytest

from data.gateways.gemini_gateway import GeminiGateway
from domain.entities.language_model_settings import LanguageModelSettings
from domain.errors import LanguageModelError

ANSWER_BODY = {"candidates": [{"content": {"parts": [{"text": "Brasília"}]}}]}
GENERATE_CONTENT_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"


def build_gateway(handler):
    return GeminiGateway(httpx.Client(transport=httpx.MockTransport(handler)))


def build_settings(**overrides):
    values = {"endpoint_url": GENERATE_CONTENT_URL, "api_key": "secret", "model_name": None}
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
        captured["url"] = str(request.url)
        return httpx.Response(200, json=ANSWER_BODY)

    build_gateway(handler).ask(build_settings(), "Capital?")

    assert captured["url"] == GENERATE_CONTENT_URL
    assert captured["headers"]["x-goog-api-key"] == "secret"
    assert "authorization" not in captured["headers"]
    assert captured["payload"] == {"contents": [{"role": "user", "parts": [{"text": "Capital?"}]}]}


def test_builds_url_from_host_and_model():
    captured = {}

    def handler(request):
        captured["url"] = str(request.url)
        return httpx.Response(200, json=ANSWER_BODY)

    settings = build_settings(endpoint_url="generativelanguage.googleapis.com", model_name="gemini-2.5-flash")
    build_gateway(handler).ask(settings, "Capital?")

    assert captured["url"] == GENERATE_CONTENT_URL


def test_joins_text_parts():
    body = {"candidates": [{"content": {"parts": [{"text": "Bra"}, {"text": "sília"}]}}]}
    gateway = build_gateway(lambda request: httpx.Response(200, json=body))

    assert gateway.ask(build_settings(), "Capital?") == "Brasília"


def test_fails_on_error_status():
    gateway = build_gateway(lambda request: httpx.Response(400, text="API key not valid"))

    with pytest.raises(LanguageModelError, match="400"):
        gateway.ask(build_settings(), "Capital?")


def test_fails_when_answer_was_blocked():
    body = {"promptFeedback": {"blockReason": "SAFETY"}}
    gateway = build_gateway(lambda request: httpx.Response(200, json=body))

    with pytest.raises(LanguageModelError, match="expected format"):
        gateway.ask(build_settings(), "Capital?")
