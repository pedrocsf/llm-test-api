import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from data.scoring.embedding_scoring_method import EmbeddingScoringMethod

MODELS_DIRECTORY = PROJECT_ROOT / "models"


def main() -> None:
    EmbeddingScoringMethod(MODELS_DIRECTORY).prepare()
    print(f"Modelo disponível em {MODELS_DIRECTORY}")


if __name__ == "__main__":
    main()
