import pathlib


def sorah_ayah_format(sorah_num: int, ayah_num: int, ext: str = "mp3") -> str:
    return f"{sorah_num:03}{ayah_num:03}.{ext}"


def path_join(dir: pathlib.Path, rest: str) -> str:
    return str(dir.joinpath(pathlib.Path(rest)).absolute())
