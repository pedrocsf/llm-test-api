import re
import string
import unicodedata

ENGLISH_ARTICLES = re.compile(r"\b(a|an|the)\b")
ASCII_PUNCTUATION = frozenset(string.punctuation)
WORD_PATTERN = re.compile(r"\w+")


def _is_punctuation(character: str) -> bool:
    return character in ASCII_PUNCTUATION or unicodedata.category(character).startswith("P")


def normalize_answer(text: str) -> str:
    lowered = text.lower()
    without_punctuation = "".join(character for character in lowered if not _is_punctuation(character))
    without_articles = ENGLISH_ARTICLES.sub(" ", without_punctuation)
    return " ".join(without_articles.split())


def normalized_tokens(text: str) -> list[str]:
    return normalize_answer(text).split()


def word_tokens(text: str) -> list[str]:
    return WORD_PATTERN.findall(text.lower())
