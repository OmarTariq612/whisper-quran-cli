from pydantic.dataclasses import dataclass
from pydantic import computed_field
from typing import Iterable
from sys import stderr


@dataclass
class WERInfo:
    insertions: int
    deletions: int
    hits: int
    substitutions: int
    wer: float


def merge_wer_info(entries: Iterable[WERInfo]) -> WERInfo:
    insertions = 0
    deletions = 0
    hits = 0
    substitutions = 0

    for entry in entries:
        insertions += entry.insertions
        deletions += entry.deletions
        hits += entry.hits
        substitutions += entry.substitutions

    wer = (insertions + deletions + substitutions) / (deletions + substitutions + hits)

    return WERInfo(
        insertions=insertions,
        deletions=deletions,
        hits=hits,
        substitutions=substitutions,
        wer=wer,
    )


@dataclass
class Benchmark:
    duration: float
    processing_time: float


@dataclass
class OutputPartEntry:
    number: int
    pred_text: str
    ref_text: str
    wer_info: WERInfo
    bench_data: Benchmark


@dataclass
class OutputSorahEntry:
    sorah_num: int
    parts: list[OutputPartEntry]

    @computed_field
    def wer_info(self) -> WERInfo:
        try:
            wer_info = merge_wer_info(map(lambda part: part.wer_info, self.parts))  # type: ignore
            return wer_info
        except Exception as e:
            print(e, file=stderr)
        return WERInfo(insertions=0, deletions=0, hits=0, substitutions=0, wer=1)


@dataclass
class TotalEntry:
    sorahs: list[OutputSorahEntry]

    @computed_field
    def wer_info(self) -> WERInfo:
        try:
            wer_info = merge_wer_info(map(lambda sorah: sorah.wer_info, self.sorahs))  # type: ignore
            return wer_info
        except Exception as e:
            print(e, file=stderr)
        return WERInfo(insertions=0, deletions=0, hits=0, substitutions=0, wer=1)
