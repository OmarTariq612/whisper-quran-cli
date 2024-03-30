from pathlib import Path
from typing import Final
import torch


DEVICE: Final[str] = "cuda" if torch.cuda.is_available() else "cpu"


def path_join(dir: Path, rest: str) -> str:
    return str(dir.joinpath(Path(rest)).absolute())
