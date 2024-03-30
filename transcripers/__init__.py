from typing import Final, Type
from .base_transcriper import BaseTranscriper
from .quran_transcriper import QuranComTranscriper
from .ayat_transcriper import AyatTranscriper


mapping: Final[dict[str, Type[BaseTranscriper]]] = {
    "QuranComTranscriper": QuranComTranscriper,
    "AyatTranscriper": AyatTranscriper,
}
