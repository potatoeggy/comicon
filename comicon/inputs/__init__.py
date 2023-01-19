from pathlib import Path
from typing import Callable, Iterator, Literal

from .. import cirtools
from . import cbz, cir, epub, pdf

SupportedInputs = Literal["cbz", "epub", "pdf", "cir"]
InputFn = Callable[[Path, Path], Iterator[str | int]]

INPUT_FN_MAP: dict[SupportedInputs, InputFn] = {
    "cbz": cbz.create_cir,
    "epub": epub.create_cir,
    "pdf": pdf.create_cir,
    "cir": cir.create_cir,
}


def create_cir(
    path: Path | str, dest: Path | str, ext: SupportedInputs, validate: bool = True
) -> None:
    """
    Create a CIR from the given path.
    """
    for _ in create_cir_progress(path, dest, ext, validate):
        ...


def create_cir_progress(
    path: Path | str, dest: Path | str, ext: SupportedInputs, validate: bool = True
) -> Iterator[str | int]:
    """
    The first thing returns the number of images (int)
    After, it returns filenames (str)
    """
    path = Path(path)
    dest = Path(dest)
    yield from INPUT_FN_MAP[ext](path, dest)

    if len(list(dest.iterdir())) > 0:
        raise OSError(f"Cannot convert to non-empty folder {dest}.")
    if validate:
        cirtools.validate_cir(dest)
