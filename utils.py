import pathlib
from typing import Iterable
from entrytypes import WERInfo


def sorah_ayah_format(sorah_num: int, ayah_num: int, ext: str = "mp3") -> str:
    return f"{sorah_num:03}{ayah_num:03}.{ext}"


def path_join(dir: pathlib.Path, rest: str) -> str:
    return str(dir.joinpath(pathlib.Path(rest)).absolute())


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
