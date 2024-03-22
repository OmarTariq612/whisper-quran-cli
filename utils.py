from pathlib import Path


def sorah_part_format(sorah_num: int, part_num: int, ext: str = "mp3") -> str:
    return f"{sorah_num:03}-{part_num:06}.{ext}"


def path_join(dir: Path, rest: str) -> str:
    return str(dir.joinpath(Path(rest)).absolute())
