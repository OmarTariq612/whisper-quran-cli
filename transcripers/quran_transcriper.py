from pydantic import BaseModel, RootModel, computed_field
from enum import Enum
import json
from pathlib import Path
from jiwer import process_words  # type: ignore
from .output_types import *
from .utils import path_join, DEVICE, count_with_diacritics, Counter
from .base_transcriper import BaseTranscriper
from .transcribe import Model


class Waqf(str, Enum):
    EMPTY = "empty"
    LAAZIM = "laazim"
    WAQF_AWLAA = "waqf-awlaa"
    JAAIZ = "jaaiz"
    WASL_AWLAA = "wasl-awlaa"
    MUAANAQAH = "muaanaqah"
    SAKTA = "sakta"
    FORBIDDEN = "forbidden"
    RAS_AYAH = "ras-ayah"


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
    starting_ayah_number: int
    ending_ayah_number: int
    cutting_blindly: bool
    segments: list[Segment]

    @computed_field
    def duration(self) -> float:
        return self.to_ms - self.from_ms

    def _to_whisper_timestamps(self, ms: float) -> str:
        return f"{round((ms - self.from_ms) / 1000 / 0.02) * 0.02:.2f}"

    @computed_field
    def text(self) -> str:
        texts = [segment.word for segment in self.segments]
        beginning = self._to_whisper_timestamps(self.segments[0].start_ms)
        end = self._to_whisper_timestamps(self.segments[-1].end_ms)
        return f'<|{beginning}|>{" ".join(texts)}<|{end}|>'

    @computed_field
    def clear_text(self) -> str:
        return " ".join(map(lambda segment: segment.word, self.segments))


class Sorah(RootModel):
    root: list[Part]


class SheikhInfo(RootModel):
    root: dict[str, Sorah]


def load_sheikh_info(path: Path) -> SheikhInfo:
    with open(path, "r", encoding="utf-8") as file:
        _json = json.load(file)

    return SheikhInfo.model_validate(_json)


def sorah_part_format(sorah_num: int, part_num: int, ext: str = "mp3") -> str:
    return f"{sorah_num:03}-{part_num:06}.{ext}"


class QuranComTranscriper(BaseTranscriper):
    def __init__(self, metadata_path: str, audio_path: str):
        super().__init__(metadata_path=metadata_path, audio_path=audio_path)

    def transcribe(
        self,
        *,
        model_id: str,
        model_constructor: Model,
        normalize_text: bool = True,
        from_sorah: int = 1,
        to_sorah: int = 114,
        device: str = DEVICE,
    ) -> tuple[TotalEntry, list[OutputSorahErrorsEntry]]:
        sheikh_info = load_sheikh_info(self.metadata_path)
        total_entry = TotalEntry(sorahs=[])
        sorahs_errors: list[OutputSorahErrorsEntry] = []

        total_counter = Counter()
        with_diacritics_counter = Counter()

        model = model_constructor.construct_model(
            model_id,
            device=device,
            fn=count_with_diacritics(total_counter, with_diacritics_counter),
        )

        for sorah_num in range(from_sorah, to_sorah + 1):
            sorah_num_str = str(sorah_num)
            sorah_entry = OutputSorahEntry(sorah_num=sorah_num, parts=[])
            curr_sorah_errors: OutputSorahErrorsEntry = OutputSorahErrorsEntry(
                sorah_num=sorah_num, parts=[]
            )

            for part in sheikh_info.root[sorah_num_str].root:
                audio_file_path = path_join(
                    self.audio_path, sorah_part_format(sorah_num, part.number)
                )

                duration = part.duration / 1000  # type: ignore

                try:
                    prediction_text, processing_time = model(
                        audio_file_path, normalize_text=normalize_text
                    )
                except Exception as e:
                    curr_sorah_errors.parts.append(
                        OutputPartErrorEntry(number=part.number, error_msg=str(e))
                    )
                    continue

                word_output = process_words(
                    hypothesis=prediction_text, reference=part.clear_text  # type: ignore
                )

                part_entry = OutputPartEntry(
                    number=part.number,
                    pred_text=prediction_text,  # type: ignore
                    ref_text=part.clear_text,  # type: ignore
                    wer_info=WERInfo(
                        insertions=word_output.insertions,
                        deletions=word_output.deletions,
                        hits=word_output.hits,
                        substitutions=word_output.substitutions,
                        wer=word_output.wer,
                    ),
                    bench_data=Benchmark(
                        duration_s=duration, processing_time_s=processing_time
                    ),
                )

                sorah_entry.parts.append(part_entry)

            total_entry.sorahs.append(sorah_entry)

            if len(curr_sorah_errors.parts) > 0:
                sorahs_errors.append(curr_sorah_errors)

        print(f"Total count: {total_counter.current_value()}")
        print(f"With diacritics count: {with_diacritics_counter.current_value()}")
        print(
            f"Percentage of with diacritics to total count: {with_diacritics_counter.current_value() / total_counter.current_value() * 100}%"
        )

        return total_entry, sorahs_errors
