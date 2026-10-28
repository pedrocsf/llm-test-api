from collections.abc import Mapping
from dataclasses import dataclass

DEMO_DATASET_NAME = "demo-dataset.json"
DEMO_ENDPOINT = "http://127.0.0.1:1234/v1/chat/completions"
DEMO_BADGE_TEXT = "DEMO · sample data"
DEMO_CORPUS_BLEU_SCORE = 0.433


@dataclass(frozen=True)
class DemoEntry:
    identifier: str
    question: str
    expected_answer: str
    given_answer: str
    response_seconds: float
    scores: Mapping[str, float]


DEMO_ENTRIES = (
    DemoEntry(
        "1",
        "Qual é a capital da França?",
        "A capital da França é Paris.",
        "A capital da França é Paris.",
        0.42,
        {"embedding": 1.0, "exact_match": 1.0, "token_f1": 1.0, "rouge_1": 1.0, "rouge_2": 1.0, "rouge_l": 1.0, "bleu": 1.0},
    ),
    DemoEntry(
        "2",
        "Quantos planetas existem no Sistema Solar?",
        "O Sistema Solar tem oito planetas.",
        "Existem oito planetas no Sistema Solar.",
        0.88,
        {"embedding": 0.989, "exact_match": 0.0, "token_f1": 0.667, "rouge_1": 0.667, "rouge_2": 0.4, "rouge_l": 0.333, "bleu": 0.196},
    ),
    DemoEntry(
        "3",
        "Quem escreveu Dom Casmurro?",
        "Dom Casmurro foi escrito por Machado de Assis.",
        "Machado de Assis escreveu Dom Casmurro.",
        1.35,
        {"embedding": 0.973, "exact_match": 0.0, "token_f1": 0.714, "rouge_1": 0.714, "rouge_2": 0.5, "rouge_l": 0.429, "bleu": 0.242},
    ),
    DemoEntry(
        "4",
        "Qual é o maior oceano do mundo?",
        "O maior oceano do mundo é o Oceano Pacífico.",
        "O maior oceano do mundo é o Oceano Pacífico.",
        1.12,
        {"embedding": 1.0, "exact_match": 1.0, "token_f1": 1.0, "rouge_1": 1.0, "rouge_2": 1.0, "rouge_l": 1.0, "bleu": 1.0},
    ),
    DemoEntry(
        "5",
        "Em que ano o homem pisou na Lua pela primeira vez?",
        "O homem pisou na Lua pela primeira vez em 1969.",
        "Em 1969, com a missão Apollo 11.",
        0.37,
        {"embedding": 0.614, "exact_match": 0.0, "token_f1": 0.25, "rouge_1": 0.235, "rouge_2": 0.133, "rouge_l": 0.235, "bleu": 0.045},
    ),
    DemoEntry(
        "6",
        "Qual é a fórmula química da água?",
        "A fórmula química da água é H2O.",
        "A fórmula química da água é H2O.",
        0.41,
        {"embedding": 1.0, "exact_match": 1.0, "token_f1": 1.0, "rouge_1": 1.0, "rouge_2": 1.0, "rouge_l": 1.0, "bleu": 1.0},
    ),
    DemoEntry(
        "7",
        "Quantos lados tem um hexágono?",
        "Um hexágono tem seis lados.",
        "Seis.",
        0.95,
        {"embedding": 0.095, "exact_match": 0.0, "token_f1": 0.333, "rouge_1": 0.333, "rouge_2": 0.0, "rouge_l": 0.333, "bleu": 0.068},
    ),
    DemoEntry(
        "8",
        "Qual é o rio mais extenso do Brasil?",
        "O rio mais extenso do Brasil é o Amazonas.",
        "O rio Amazonas é o mais extenso do Brasil.",
        0.71,
        {"embedding": 0.993, "exact_match": 0.0, "token_f1": 1.0, "rouge_1": 1.0, "rouge_2": 0.625, "rouge_l": 0.667, "bleu": 0.375},
    ),
    DemoEntry(
        "9",
        "Quem pintou a Mona Lisa?",
        "A Mona Lisa foi pintada por Leonardo da Vinci.",
        "A Mona Lisa foi pintada por Michelangelo.",
        0.58,
        {"embedding": 0.795, "exact_match": 0.0, "token_f1": 0.714, "rouge_1": 0.75, "rouge_2": 0.714, "rouge_l": 0.75, "bleu": 0.551},
    ),
    DemoEntry(
        "10",
        "Qual é a raiz quadrada de 144?",
        "A raiz quadrada de 144 é 12.",
        "12",
        1.64,
        {"embedding": 0.513, "exact_match": 0.0, "token_f1": 0.286, "rouge_1": 0.25, "rouge_2": 0.0, "rouge_l": 0.25, "bleu": 0.001},
    ),
    DemoEntry(
        "11",
        "Qual é o idioma mais falado no Brasil?",
        "O idioma mais falado no Brasil é o português.",
        "",
        2.31,
        {"embedding": 0.0, "exact_match": 0.0, "token_f1": 0.0, "rouge_1": 0.0, "rouge_2": 0.0, "rouge_l": 0.0, "bleu": 0.0},
    ),
    DemoEntry(
        "12",
        "Qual é o ponto de ebulição da água ao nível do mar?",
        "A água ferve a 100 graus Celsius ao nível do mar.",
        "A água ferve a 100 °C ao nível do mar.",
        1.08,
        {"embedding": 0.978, "exact_match": 0.0, "token_f1": 0.824, "rouge_1": 0.857, "rouge_2": 0.737, "rouge_l": 0.857, "bleu": 0.641},
    ),
)
