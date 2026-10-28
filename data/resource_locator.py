import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def resolve_resource_path(relative_path: str) -> Path:
    base_directory = Path(getattr(sys, "_MEIPASS", PROJECT_ROOT))
    return base_directory / relative_path
