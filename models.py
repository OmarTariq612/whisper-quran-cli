from pydantic import BaseModel, RootModel, computed_field
from enum import Enum
import json


class Waqf(str, Enum):
    EMPTY = "empty"
    LAAZIM = "laazim"
    WAQF_AWLAA = "waqf-awlaa"
    JAAIZ = "jaaiz"
    WASL_AWLAA = "wasl-awlaa"
    MUAANAQAH = "muaanaqah"
    SAKTA = "sakta"
    FORBIDDEN = "forbidden"


class Segment(BaseModel):
    index: int
    start_ms: float
    end_ms: float
    word: str
    waqf: Waqf

    @computed_field
    def duration(self) -> float:
        return self.end_ms - self.start_ms


class Part(BaseModel):
    from_ms: float
    to_ms: float
    number: int
    cutting_blindly: bool
    segments: list[Segment]

    @computed_field
    def duration(self) -> float:
        return self.to_ms - self.from_ms

    def _to_whisper_timestamps(self, ms: float) -> str:
        return f"{round((ms - self.from_ms) / 1000 / 0.02) * 0.02:.2f}"

    @computed_field
    def text_with_timestamps(self) -> str:
        texts = []
        for segment in self.segments:
            begining = self._to_whisper_timestamps(segment.start_ms)
            end = self._to_whisper_timestamps(segment.end_ms)
            texts.append(f"<|{begining}|>{segment.word}<|{end}|>")
        return " ".join(texts)

    @computed_field
    def clear_text(self) -> str:
        return " ".join(map(lambda segment: segment.word, self.segments))


class Ayah(RootModel):
    root: list[Part]


class Sorah(RootModel):
    root: dict[str, Ayah]


class SheikhInfo(RootModel):
    root: dict[str, Sorah]


def load_sheikh_info(path: str) -> SheikhInfo:
    with open(path, "r", encoding="utf-8") as file:
        _json = json.load(file)

    return SheikhInfo.model_validate(_json)
