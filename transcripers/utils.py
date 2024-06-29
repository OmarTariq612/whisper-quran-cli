from pathlib import Path
from typing import Final, Callable, Any
import torch
import re


DEVICE: Final[str] = "cuda" if torch.cuda.is_available() else "cpu"


def path_join(dir: Path, rest: str) -> str:
    return str(dir.joinpath(Path(rest)).absolute())


def remove_diacritics(text: str) -> str:
    text = re.sub(r"[ًٌٍَُِّْ]", "", text)
    return text


class Counter:
    def __init__(self, value=0):
        self.value = value

    def increment(self):
        self.value += 1

    def current_value(self):
        return self.value


def count_with_diacritics(
    total_counter: Counter, with_diacritics_counter: Counter
) -> Callable[[str], Any]:
    def fn(text: str):
        total_counter.increment()
        if remove_diacritics(text) != text:
            with_diacritics_counter.increment()

    return fn
