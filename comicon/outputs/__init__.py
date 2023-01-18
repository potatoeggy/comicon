from pathlib import Path
from typing import Callable, Iterator, Literal

from .. import cirtools
from . import cbz, cir, epub, pdf

SupportedOutputs = Literal["cbz", "epub", "pdf", "cir"]
OutputFn = Callable[[Path, Path], Iterator[str | int]]

OUTPUT_FN_MAP: dict[SupportedOutputs, OutputFn] = {
    "cbz": cbz.create_comic,
    "epub": epub.create_comic,
    "pdf": pdf.create_comic,
    "cir": cir.create_comic,
}


def create_comic(
    ir_path: Path | str, dest: Path | str, ext: SupportedOutputs, validate: bool = True
) -> None:
    for _ in create_comic_progress(ir_path, dest, ext, validate):
        ...


def create_comic_progress(
    ir_path: Path | str, dest: Path | str, ext: SupportedOutputs, validate: bool = True
) -> Iterator[str | int]:
    # TODO: make iterator for progress bar
    """
    Create a comic from the given CIR path.

    :param `cir_path`: The path to the IR folder.
    :param `dest`: The path to the destination file.
    """
    ir_path = Path(ir_path)
    dest = Path(dest)

    if validate:
        cirtools.validate_cir(ir_path)

    if dest.is_dir():
        raise IsADirectoryError(
            f"{dest} is a directory. Make sure you pass the file"
            "path to the new comic file."
        )
    yield from OUTPUT_FN_MAP[ext](ir_path, dest)
