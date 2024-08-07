from abc import ABC, abstractmethod
from .output_types import *  # type: ignore
from .utils import path_join, DEVICE  # type: ignore
from pathlib import Path
from json import dump
from pydantic import RootModel
from .transcribe import Model


class BaseTranscriper(ABC):
    def __init__(self, metadata_path: str, audio_path: str):
        self.metadata_path = Path(metadata_path)
        self.audio_path = Path(audio_path)

    @abstractmethod
    def transcribe(
        self,
        *,
        model_id: str,
        model_constructor: Model,
        normalize_text: bool,
        from_sorah: int,
        to_sorah: int,
        device: str,
    ) -> tuple[TotalEntry, list[OutputSorahErrorsEntry]]:
        pass

    def __call__(
        self,
        *,
        model_id: str,
        model_constructor: Model,
        normalize_text: bool = True,
        from_sorah: int = 1,
        to_sorah: int = 114,
        device: str = DEVICE,
        output_dir: str = ".",
        output_filename: str | None = None,
    ) -> None:
        total_entry, output_sorahs_errors = self.transcribe(
            model_id=model_id,
            model_constructor=model_constructor,
            normalize_text=normalize_text,
            from_sorah=from_sorah,
            to_sorah=to_sorah,
            device=device,
        )

        output_sorahs_errors_obj = [
            RootModel[OutputSorahErrorsEntry](sorahs_errors).model_dump()
            for sorahs_errors in output_sorahs_errors
        ]

        if output_filename is None:
            output_filename = self.audio_path.name

        output_dir_path = Path(output_dir)

        with open(
            path_join(output_dir_path, f"{output_filename}.json"),
            "w",
            encoding="utf-8",
        ) as file:
            dump(
                RootModel[TotalEntry](total_entry).model_dump(),  # type: ignore
                file,
                ensure_ascii=False,
            )

        with open(
            path_join(output_dir_path, f"{output_filename}_errors.json"),
            "w",
            encoding="utf-8",
        ) as file:
            dump(
                output_sorahs_errors_obj,
                file,
                ensure_ascii=False,
            )
