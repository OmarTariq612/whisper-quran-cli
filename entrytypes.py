from dataclasses import dataclass


@dataclass
class WERInfo:
    insertions: int
    deletions: int
    hits: int
    substitutions: int
    wer: float

    def __str__(self) -> str:
        return f"{self.insertions},{self.deletions},{self.hits},{self.substitutions},{self.wer:.4f}"


@dataclass
class BenchmarkEntry:
    duration: float
    processing_time: float

    def __str__(self) -> str:
        return f"{self.duration:.2f},{self.processing_time:.2f}"


@dataclass
class PerSorahEntry:
    sorah: int
    wer_info: WERInfo

    def __str__(self) -> str:
        return f"{self.sorah},{self.wer_info}"


@dataclass
class PerAyahEntry:
    sorah: int
    ayah: int
    bench_data: BenchmarkEntry
    pred_text: str
    ref_text: str
    wer_info: WERInfo

    def __str__(self) -> str:
        return (
            f"{self.sorah},{self.ayah},{self.pred_text},{self.ref_text},{self.bench_data},{self.wer_info}"
        )


@dataclass
class TotalEntry:
    wer_info: WERInfo

    def __str__(self) -> str:
        return f"{self.wer_info}"
