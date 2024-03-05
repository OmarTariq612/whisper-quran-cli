import click
from clicktypes import SORAH_RANGE, WHSIPER_MODEL_CHOICE


@click.command(help="generate csv files containing WER for the given input and model")
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
@click.option("--sorah-range", default="1:114", type=SORAH_RANGE)
@click.option(
    "--out-prefix",
    type=click.STRING,
)
@click.option(
    "-o",
    default=".",
    type=click.Path(file_okay=False, executable=True),
    help="output directory",
)
@click.option(
    "--device",
    "-d",
    default="cuda",
    type=str,
    help="device used to load the model",
)
def generate(
    audio_path: str,
    metadata_path: str,
    model: str,
    sorah_range: tuple[int, int],
    out_prefix: str,
    o: str,
    device: str,
):
    from transcribe import transcribe

    transcribe(
        audio_path=audio_path,
        metadata_path=metadata_path,
        model_str=model,
        from_sorah=sorah_range[0],
        to_sorah=sorah_range[1],
        output_dir=o,
        out_prefix=out_prefix,
        device=device,
    )


if __name__ == "__main__":
    generate()
