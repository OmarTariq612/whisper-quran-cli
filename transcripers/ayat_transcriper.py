from whisper.model import Whisper  # type: ignore
from whisper import load_model, load_audio  # type: ignore
import time
from pydantic import RootModel
from pathlib import Path
from jiwer import process_words  # type: ignore
from .output_types import *  # type: ignore
from .utils import path_join, DEVICE  # type: ignore
from .base_transcriper import BaseTranscriper  # type: ignore
from mutagen.mp3 import MP3
import csv


class Sorah(RootModel):
    root: list[str]


def load_metadata(path: Path) -> list[Sorah]:
    reference_texts: dict[int, list[str]] = {}
    with open(path, "r") as reference_csv_file:
        reader = csv.DictReader(reference_csv_file)
        for line in reader:
            reference_texts.setdefault(int(line["sorah"]), list()).append(line["text"])

    result: list[Sorah] = [
        Sorah(reference_texts[sorah_num]) for sorah_num in range(1, 115)
    ]

    return result


def sorah_ayah_format(sorah_num: int, ayah_num: int, ext: str = "mp3") -> str:
    return f"{sorah_num:03}-{ayah_num:03}.{ext}"


class AyatTranscriper(BaseTranscriper):
    def __init__(self, metadata_path: str, audio_path: str):
        super().__init__(metadata_path=metadata_path, audio_path=audio_path)

    def transcribe(
        self,
        *,
        model: str | Whisper,
        from_sorah: int = 1,
        to_sorah: int = 114,
        device: str = DEVICE,
    ) -> tuple[TotalEntry, list[OutputSorahErrorsEntry]]:  # type: ignore

        sorahs_ref_text = load_metadata(self.metadata_path)
        total_entry = TotalEntry(sorahs=[])  # type: ignore
        sorahs_errors: list[OutputSorahErrorsEntry] = []  # type: ignore

        if not isinstance(model, Whisper):
            print(f"loading the model to {device}")
            model = load_model(model, device=device)

        for sorah_num in range(from_sorah, to_sorah + 1):
            sorah_entry = OutputSorahEntry(sorah_num=sorah_num, parts=[])  # type: ignore
            curr_sorah_errors = list[OutputPartErrorEntry] = []  # type: ignore

            for ayah_num, ayah in enumerate(
                sorahs_ref_text[sorah_num - 1].root, start=1
            ):
                audio_file_path = path_join(
                    self.audio_path,
                    sorah_ayah_format(sorah_num=sorah_num, ayah_num=ayah_num),
                )

                duration = MP3(audio_file_path).info.length  # type: ignore
                try:
                    audio_wave = load_audio(audio_file_path)
                except Exception as e:
                    curr_sorah_errors.append(OutputPartErrorEntry(number=part.number, error_msg=str(e)))  # type: ignore
                    continue

                time_start = time.perf_counter()
                result = model.transcribe(audio_wave, language="ar")
                time_end = time.perf_counter()
                processing_time = time_end - time_start

                prediction_text = result["text"]
                word_output = process_words(
                    hypothesis=prediction_text, reference=ayah.text  # type: ignore
                )

                part_entry = OutputPartEntry(  # type: ignore
                    number=ayah_num,
                    pred_text=prediction_text,  # type: ignore
                    ref_text=ayah.text,  # type: ignore
                    wer_info=WERInfo(  # type: ignore
                        insertions=word_output.insertions,
                        deletions=word_output.deletions,
                        hits=word_output.hits,
                        substitutions=word_output.substitutions,
                        wer=word_output.wer,
                    ),
                    bench_data=Benchmark(  # type: ignore
                        duration_s=duration, processing_time_ms=processing_time
                    ),
                )

                sorah_entry.parts.append(part_entry)

            sorahs_errors.append(curr_sorah_errors)  # type: ignore
            total_entry.sorahs.append(sorah_entry)

        return total_entry, sorahs_errors
