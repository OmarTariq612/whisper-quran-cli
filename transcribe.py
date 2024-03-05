import whisper
import torch
import pathlib
from typing import Optional, Final
from utils import path_join, sorah_ayah_part_format
import time
from jiwer import process_words
from entrytypes import (
    WERInfo,
    OutputAyahEntry,
    OutputSorahEntry,
    TotalEntry,
    Benchmark,
    OutputPartEntry,
)
from models import load_sheikh_info
import json
from pydantic import RootModel


DEVICE: Final[str] = "cuda" if torch.cuda.is_available() else "cpu"


def transcribe(
    audio_path: str,
    metadata_path: str,
    model_str: str = "medium",
    from_sorah: int = 1,
    to_sorah: int = 114,
    output_dir: str = ".",
    out_prefix: Optional[str] = None,
    device: str = DEVICE,
):
    if not out_prefix:
        out_prefix = model_str

    sheikh_info = load_sheikh_info(metadata_path)
    audio_dir_path = pathlib.Path(audio_path)
    output_dir_path = pathlib.Path(output_dir)
    total_entry = TotalEntry(sorahs=[])

    print(f"loading the model to {device}")
    model = whisper.load_model(model_str, device=device)

    load_wave_errors: list[str] = []

    for sorah_num in range(from_sorah, to_sorah + 1):
        sorah_num_str = str(sorah_num)
        sorah_entry = OutputSorahEntry(sorah_num=sorah_num, ayahs=[])

        for ayah_num_str, ayah in sheikh_info.root[sorah_num_str].root.items():
            ayah_num = int(ayah_num_str)
            ayah_entry = OutputAyahEntry(ayah_num=ayah_num, parts=[])

            for part in ayah.root:
                audio_file_path = path_join(
                    audio_dir_path,
                    sorah_ayah_part_format(sorah_num, ayah_num, part.number),
                )
                duration = part.duration / 1000  # type: ignore
                try:
                    audio_wave = whisper.load_audio(audio_file_path)
                except Exception as e:
                    load_wave_errors.append(str(e))
                    continue
                time_start = time.perf_counter()
                result = model.transcribe(audio_wave, language="ar")
                time_end = time.perf_counter()
                processing_time = time_end - time_start

                prediction_text = result["text"]
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
                        duration=duration, processing_time=processing_time
                    ),
                )

                ayah_entry.parts.append(part_entry)

            sorah_entry.ayahs.append(ayah_entry)

        total_entry.sorahs.append(sorah_entry)

    with open(
        path_join(output_dir_path, f"{out_prefix}.json"),
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            RootModel[TotalEntry](total_entry).model_dump(), file, ensure_ascii=False
        )

    with open(
        path_join(output_dir_path, f"{out_prefix}_load_wave_errors.json"),
        "w",
        encoding="utf-8",
    ) as errors_file:
        json.dump(load_wave_errors, errors_file, ensure_ascii=False)
