from typing import Protocol, Union, Callable, Any, Optional
from pathlib import Path
from .utils import DEVICE, remove_diacritics  # type: ignore
from whisper import load_model, load_audio  # type: ignore
import time
from transformers import pipeline  # type: ignore
import torch
import torchaudio  # type: ignore
import torchaudio.transforms as at  # type: ignore
import re


def load_wave(wave_path, sample_rate: int = 16000) -> torch.Tensor:
    waveform, sr = torchaudio.load(wave_path, normalize=True, backend="ffmpeg")
    if sample_rate != sr:
        waveform = at.Resample(sr, sample_rate)(waveform)
    return waveform


class Transcribe(Protocol):
    def __call__(
        self, audio_file_path: Union[str, Path], normalize_text: bool = True
    ) -> tuple[str, float]: ...


class Model(Protocol):
    def construct_model(
        self,
        path: Union[str, Path],
        device: str = DEVICE,
        fn: Optional[Callable[[str], Any]] = None,
    ) -> Transcribe: ...


class OpenAIWhisperModel:
    def construct_model(
        self,
        path: Union[str, Path],
        device: str = DEVICE,
        fn: Optional[Callable[[str], Any]] = None,
    ) -> Transcribe:
        path = str(path)
        self.model = load_model(path, device=device)
        self.fn = fn
        return self

    def __call__(
        self, audio_file_path: Union[str, Path], normalize_text: bool = True
    ) -> tuple[str, float]:
        audio_file_path = str(audio_file_path)
        audio_wave = load_audio(audio_file_path)
        time_start = time.perf_counter()
        result = self.model.transcribe(audio_wave, language="ar")
        time_end = time.perf_counter()
        processing_time = time_end - time_start

        if self.fn:
            self.fn(result["text"])

        return remove_diacritics(result["text"]) if normalize_text else result["text"], processing_time  # type: ignore


class TransformersWhisperModel:
    def construct_model(
        self,
        path: Union[str, Path],
        device: str = DEVICE,
        fn: Optional[Callable[[str], Any]] = None,
    ) -> Transcribe:
        path = str(path)
        self.model = pipeline(
            "automatic-speech-recognition", model=path, chunk_length_s=30, device=device
        )

        self.fn = fn

        return self

    def __call__(
        self, audio_file_path: Union[str, Path], normalize_text: bool = True
    ) -> tuple[str, float]:
        audio_wave = load_wave(audio_file_path)[0]
        time_start = time.perf_counter()
        result = self.model(audio_wave.numpy())
        time_end = time.perf_counter()
        processing_time = time_end - time_start

        if self.fn:
            self.fn(result["text"])

        return remove_diacritics(result["text"]) if normalize_text else result["text"], processing_time  # type: ignore
