from pathlib import Path
from typing import Callable, Literal

from . import cbz, cir, epub, pdf

SupportedOutputs = Literal["cbz", "epub", "pdf", "cir"]
OutputFn = Callable[[Path, Path], None]

OUTPUT_FN_MAP: dict[SupportedOutputs, OutputFn] = {
    "cbz": cbz.create_comic,
    "epub": epub.create_comic,
    "pdf": pdf.create_comic,
    "cir": cir.create_comic,
}


def create_comic(ir_path: Path | str, dest: Path | str, ext: SupportedOutputs) -> None:
    # TODO: make iterator for progress bar
    """
    Create a comic from the given CIR path.

    :param `cir_path`: The path to the IR folder.
    :param `dest`: The path to the destination file.
    """
    ir_path = Path(ir_path)
    dest = Path(dest)
    return OUTPUT_FN_MAP[ext](ir_path, dest)
