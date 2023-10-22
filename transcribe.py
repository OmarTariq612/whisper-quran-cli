import whisper
from pyarabic import araby
from dataclasses import dataclass
import csv
import evaluate
import pathlib
from typing import Optional
from utils import path_join, sorah_ayah_format


@dataclass
class PerSorahEntry:
    sorah: int
    wer: float
    num_words_reference: int

    def __str__(self) -> str:
        return f"{self.sorah},{self.wer:.4f},{self.num_words_reference}"


@dataclass
class PerAyahEntry:
    sorah: int
    ayah: int
    wer: float
    num_words_reference: int

    def __str__(self) -> str:
        return f"{self.sorah},{self.ayah},{self.wer:.4f},{self.num_words_reference}"


@dataclass
class TotalEntry:
    wer: float
    num_words_reference: int

    def __str__(self) -> str:
        return f"{self.wer:.4f},{self.num_words_reference}"


def transcribe(
    audio_path: str,
    text_csv_path: str,
    model_str: str = "medium",
    from_sorah: int = 1,
    to_sorah: int = 114,
    output_dir: str = ".",
    out_prefix: Optional[str] = None,
    log_level: str = "normal",
    do_benchmark: bool = False,
):
    if not out_prefix:
        out_prefix = model_str

    reference_texts: dict[int, list[str]] = {}
    with open(text_csv_path, "r") as reference_csv_file:
        reader = csv.DictReader(reference_csv_file)
        for line in reader:
            # TODO: currently we are depending on the order is there a better way??
            reference_texts.setdefault(int(line["sorah"]), list()).append(line["text"])

    audio_dir_path = pathlib.Path(audio_path)
    output_dir_path = pathlib.Path(output_dir)

    for sorah_num in range(from_sorah, to_sorah + 1):  # inclusive
        if not sorah_num in reference_texts:
            raise ValueError(
                f"the given text csv reference doesn't have sorah({sorah_num})"
            )
        if not audio_dir_path.joinpath(
            pathlib.Path(sorah_ayah_format(sorah_num=sorah_num, ayah_num=1))
        ).is_file():
            raise ValueError(f"the given audio path doesn't have sorah({sorah_num})")

    model = whisper.load_model(model_str)
    wer_module = evaluate.load("wer")
    per_sorah: list[PerSorahEntry] = []
    per_ayah: list[PerAyahEntry] = []
    per_ayah_index = 0

    for sorah_num in range(from_sorah, to_sorah + 1):  # inclusive
        for ayah_num, ayah_ref_text in enumerate(reference_texts[sorah_num], start=1):
            result = model.transcribe(
                path_join(
                    audio_dir_path,
                    sorah_ayah_format(sorah_num=sorah_num, ayah_num=ayah_num),
                )
            )
            prediction_text = araby.strip_diacritics(result["text"])
            if log_level == "verbose":
                print(prediction_text)
            wer: float = wer_module.compute(predictions=[prediction_text], references=[ayah_ref_text])  # type: ignore
            per_ayah.append(
                PerAyahEntry(sorah_num, ayah_num, wer, len(ayah_ref_text.split()))
            )

        total_num = 0
        total_denum = 0
        for i in range(per_ayah_index, len(per_ayah)):
            total_num += per_ayah[i].wer * per_ayah[i].num_words_reference
            total_denum += per_ayah[i].num_words_reference

        per_sorah.append(PerSorahEntry(sorah_num, total_num / total_denum, total_denum))
        per_ayah_index = len(per_ayah)

    with open(
        path_join(output_dir_path, f"{out_prefix}_per_ayah.csv"),
        "w",
    ) as per_ayah_file:
        per_ayah_file.write("sorah,ayah,wer,num_words_reference\n")
        for entry in per_ayah:
            per_ayah_file.write(f"{entry}\n")

    with open(
        path_join(output_dir_path, f"{out_prefix}_per_sorah.csv"), "w"
    ) as per_sorah_file:
        per_sorah_file.write("sorah,wer,num_words_reference\n")
        for entry in per_sorah:
            per_sorah_file.write(f"{entry}\n")

    total_num = 0
    total_denum = 0
    for entry in per_sorah:
        total_num += entry.wer * entry.num_words_reference
        total_denum += entry.num_words_reference

    total_entry = TotalEntry(total_num / total_denum, total_denum)

    with open(path_join(output_dir_path, f"{out_prefix}_total.csv"), "w") as total_file:
        total_file.write("wer,num_words_reference\n")
        total_file.write(f"{total_entry}\n")
