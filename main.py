import click
from clicktypes import SORAH_RANGE, WHSIPER_MODEL_CHOICE


@click.command(help="transcribe sorahs in the given range + the WER")
@click.argument(
    "transcriber",
    type=click.Choice(["QuranComTranscriper", "AyatTranscriper"], case_sensitive=False),
)
@click.argument(
    "metadata-path", type=click.Path(file_okay=True, dir_okay=False, exists=True)
)
@click.argument(
    "audio-path", type=click.Path(file_okay=False, exists=True, executable=True)
)
@click.option(
    "--model",
    default="medium",
    type=WHSIPER_MODEL_CHOICE,
    help="multilingual model used for transcribing (default: medium)",
)
@click.option(
    "--model-constructor",
    default="OpenAIWhisperModel",
    type=click.Choice(
        ["OpenAIWhisperModel", "TransformersWhisperModel"], case_sensitive=False
    ),
    help="model variant to use (openai-whisper or transformers)",
)
@click.option(
    "--normalize-text",
    default=True,
    type=bool,
    help="whether to normalize the output text of the model before calculating WER or not",
)
@click.option("--sorah-range", default="1:114", type=SORAH_RANGE)
@click.option(
    "--device",
    "-d",
    default="cuda",
    type=str,
    help="device used to load the model",
)
@click.option(
    "-o",
    default=".",
    type=click.Path(file_okay=False, executable=True),
    help="output directory",
)
@click.option(
    "--output-filename",
    type=click.STRING,
)
def generate(
    transcriber: str,
    audio_path: str,
    metadata_path: str,
    model: str,
    model_constructor: str,
    normalize_text: bool,
    sorah_range: tuple[int, int],
    device: str,
    o: str,
    output_filename: str,
):
    from transcripers import mapping, constructor_mapping

    cls = mapping[transcriber]
    model_constructor_obj = constructor_mapping[model_constructor]()

    obj = cls(metadata_path=metadata_path, audio_path=audio_path)
    obj(
        model_id=model,
        model_constructor=model_constructor_obj,
        normalize_text=normalize_text,
        from_sorah=sorah_range[0],
        to_sorah=sorah_range[1],
        device=device,
        output_dir=o,
        output_filename=output_filename,
    )


if __name__ == "__main__":
    generate()
