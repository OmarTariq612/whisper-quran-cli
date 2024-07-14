import click
from typing import Final
import requests  # type: ignore


class SorahRange(click.ParamType):
    name = "from-to inclusive (ex: 1:114)"

    def convert(self, value: str, param, ctx):
        if not ":" in value:
            self.fail(f"{value} is not a valid SorahRange")

        parts = value.split(":")
        if len(parts) != 2:
            self.fail(f"{value} is not a valid SorahRange")

        if not parts[0].isdecimal() or not parts[1].isdecimal():
            self.fail(
                f"invalid range: parts must be decimal between 1 and 114: {parts}"
            )

        minimum = int(parts[0], base=10)
        maximum = int(parts[1], base=10)

        if minimum < 1:
            self.fail(f"minimum({minimum}) must be > 0")
        if maximum > 114:
            self.fail(f"maximum({maximum}) must be <= 114")
        if minimum > maximum:
            self.fail(f"minimum({minimum}) must be <= maximum({maximum})")

        return (minimum, maximum)


SORAH_RANGE = SorahRange()


class WhisperModelChoice(click.ParamType):
    name = "whisper-model-choice"

    Models: Final[set[str]] = {
        "tiny",
        "base",
        "small",
        "medium",
        "large",
        "large-v1",
        "large-v2",
        "large-v3",
    }

    def convert(self, value: str, param, ctx):
        if (
            value in WhisperModelChoice.Models
            or requests.get(f"https://huggingface.co/{value}").status_code == 200
        ):
            return value

        return click.Path(exists=True, dir_okay=False).convert(value, param, ctx)

    def get_metavar(self, param: click.Parameter) -> str:
        return "[name|checkpoint_path]"


WHSIPER_MODEL_CHOICE = WhisperModelChoice()
