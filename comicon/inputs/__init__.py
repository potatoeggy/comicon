from pathlib import Path
from typing import Callable, Iterator, Literal, cast, get_args

from .. import cirtools
from . import cbz, cir, epub, pdf

SupportedInputs = Literal["cbz", "epub", "pdf", "cir"]
InputFn = Callable[[Path, Path], Iterator[str | int]]

SupportedInputList: tuple[SupportedInputs] = get_args(SupportedInputs)  # type: ignore

INPUT_FN_MAP: dict[SupportedInputs, InputFn] = {
    "cbz": cbz.create_cir,
    "epub": epub.create_cir,
    "pdf": pdf.create_cir,
    "cir": cir.create_cir,
}


def create_cir(
    path: Path | str,
    dest: Path | str,
    ext: SupportedInputs | None = None,
    validate: bool = True,
) -> None:
    """
    Create a CIR from the given path.

    :param `path`: The path to the comic file.
    :param `dest`: The path to the destination folder.
    :param `ext`: An optional file extension string denoting the
    desired file extension.
    :param `validate`: Whether to validate the CIR after creation.
    """
    for _ in create_cir_progress(path, dest, ext, validate):
        ...


def create_cir_progress(
    path: Path | str,
    dest: Path | str,
    ext: SupportedInputs | None = None,
    validate: bool = True,
) -> Iterator[str | int]:
    """
    The first thing returns the number of images (int)
    After, it returns filenames (str)
    """
    path = Path(path)
    dest = Path(dest)

    # try to guess ext
    inferred_ext = path.suffix.lower().split(".")[-1]
    if not ext and inferred_ext not in get_args(SupportedInputs):
        raise ValueError(f"Could not infer a supported input extension ({inferred_ext})")

    inferred_ext = cast(SupportedInputs, inferred_ext)

    if len(list(dest.iterdir())) > 0:
        raise OSError(f"Cannot convert to non-empty folder {dest}.")

    yield from INPUT_FN_MAP[ext or inferred_ext](path, dest)

    if validate:
        cirtools.validate_cir(dest)
