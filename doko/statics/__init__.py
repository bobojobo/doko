"""Loading the statics."""

from pathlib import Path
from fastapi.staticfiles import StaticFiles


def statics() -> StaticFiles:
    return StaticFiles(directory=Path(__file__).parent)


PATH: str = "/statics"
NAME: str = "statics"
