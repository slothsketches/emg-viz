import pathlib
import typing as t


def load_from_sample(path: t.Union[pathlib.Path, str]):
    if isinstance(path, str):
        path = pathlib.Path(path)
        path.resolve(strict=True)

    for line in map(str.strip, path.read_text().split("\n")):
        if not line:
            continue
        yield int(line[29:])
