from dataclasses import dataclass


@dataclass(frozen=True)
class LanguageModelSettings:
    endpoint_url: str
    api_key: str | None = None
    model_name: str | None = None
