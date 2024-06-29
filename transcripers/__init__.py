from typing import Final, Type, Callable
from .base_transcriper import BaseTranscriper
from .quran_transcriper import QuranComTranscriper
from .ayat_transcriper import AyatTranscriper
from .transcribe import OpenAIWhisperModel, TransformersWhisperModel, Model


mapping: Final[dict[str, Type[BaseTranscriper]]] = {
    "QuranComTranscriper": QuranComTranscriper,
    "AyatTranscriper": AyatTranscriper,
}


# def model_with_count(cls) -> tuple[Callable, Callable, Callable]:
#     total_count = 0
#     with_diacritics_count = 0

#     def current_total_count():
#         return total_count

#     def current_with_diacritics():
#         return with_diacritics_count

#     def fn(text):
#         nonlocal total_count, with_diacritics_count
#         total_count += 1
#         if remove_diacritics(text) != text:
#             with_diacritics_count += 1

#     def func(*args, **kwargs):
#         kwargs.setdefault("fn", fn)
#         return cls.construct_model(
#             *args,
#             **kwargs,
#         )

#     return func, current_total_count, current_with_diacritics


constructor_mapping: dict[str, Type[Model]] = {
    "OpenAIWhisperModel": OpenAIWhisperModel,
    "TransformersWhisperModel": TransformersWhisperModel,
}
