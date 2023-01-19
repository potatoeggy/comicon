import tempfile
from pathlib import Path
from typing import Iterator

from .inputs import create_cir_progress
from .outputs import create_comic_progress


def convert(first: Path | str, dest: Path | str) -> None:
    for _ in convert_progress(first, dest):
        ...


def convert_progress(first: Path | str, dest: Path | str) -> Iterator[str | int]:
    first = Path(first)
    dest = Path(dest)

    with tempfile.TemporaryDirectory() as fp:
        tempdir = Path(fp)

        yield from create_cir_progress(first, tempdir)
        yield from create_comic_progress(tempdir, dest)
