import click
from clicktypes import SORAH_RANGE, WHSIPER_MODEL_CHOICE
from merge import merge as m
from audiomentations import TimeStretch
from typing import Optional

@click.group()
def main():
    pass


@main.command(help="generate csv files containing WER for the given input and model")
@click.argument(
    "text-csv-path", type=click.Path(dir_okay=False, exists=True, readable=True)
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
    "--time-stretch",
    default=None,
    type=(float, float, float),
    help="min_rate max_rate probability",
)
@click.option("--sorah-range", default="1:114", type=SORAH_RANGE)
@click.option(
    "--out-prefix",
    type=click.STRING,
)
@click.option(
    "--log-level",
    default="normal",
    type=click.Choice(("normal", "verbose")),
    help="determine the logging level (default: normal)",
)
@click.option(
    "-o",
    default=".",
    type=click.Path(file_okay=False, executable=True),
    help="output directory",
)
@click.option(
    "--bench",
    "-b",
    default=False,
    is_flag=True,
    type=click.BOOL,
    help="export benchmark info to a file",
)
@click.option(
    "--device",
    "-d",
    default="cuda",
    type=str,
    help="device used to load the model",
)
def generate(
    text_csv_path: str,
    audio_path: str,
    model: str,
    time_stretch: tuple[float, float, float],
    sorah_range: tuple[int, int],
    out_prefix: str,
    log_level: str,
    o: str,
    bench: bool,
    device: str
):
    from transcribe import transcribe

    time_stretch_obj: Optional[TimeStretch] = None
    if time_stretch:
        time_stretch_obj = TimeStretch(
            min_rate=time_stretch[0],
            max_rate=time_stretch[1],
            leave_length_unchanged=False,
            p=time_stretch[2],
        )

    transcribe(
        audio_path=audio_path,
        text_csv_path=text_csv_path,
        model_str=model,
        transform=time_stretch_obj,
        from_sorah=sorah_range[0],
        to_sorah=sorah_range[1],
        output_dir=o,
        out_prefix=out_prefix,
        log_level=log_level,
        do_benchmark=bench,
        device=device,
    )


@main.command(help="merge multiple csv files into one containing WER as a total")
@click.argument(
    "src",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    nargs=-1,
    required=True,
)
@click.option("--out-prefix", default="merged", type=click.STRING)
@click.option(
    "-o", default=".", type=click.Path(exists=True, file_okay=False, executable=True)
)
def merge(src: tuple[str, ...], out_prefix: str, o: str):
    m(srcs=src, out_prefix=out_prefix, output_dir=o)


if __name__ == "__main__":
    main()
