from urllib.parse import urlsplit, urlunsplit

import httpx

from domain.errors import LanguageModelError

ERROR_BODY_PREVIEW_LENGTH = 300
HTTP_URL_SCHEME = "http://"
HTTPS_URL_SCHEME = "https://"
SCHEME_SEPARATOR = "://"
ROOT_PATHS = ("", "/")


def normalize_url(endpoint_url: str, default_scheme: str = HTTP_URL_SCHEME) -> str:
    cleaned_url = endpoint_url.strip()
    if SCHEME_SEPARATOR in cleaned_url:
        return cleaned_url
    return default_scheme + cleaned_url


def with_default_path(url: str, default_path: str) -> str:
    parts = urlsplit(url)
    if parts.path not in ROOT_PATHS:
        return url
    return urlunsplit(parts._replace(path=default_path))


def post_json(client: httpx.Client, url: str, payload: dict, headers: dict) -> httpx.Response:
    try:
        response = client.post(url, json=payload, headers=headers)
    except httpx.HTTPError as error:
        raise LanguageModelError(f"Failed to connect to {url}: {error}") from error
    if response.is_error:
        preview = response.text[:ERROR_BODY_PREVIEW_LENGTH]
        raise LanguageModelError(f"The LLM responded with status {response.status_code}: {preview}")
    return response
