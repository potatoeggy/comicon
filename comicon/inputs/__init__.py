from pathlib import Path
from typing import Callable, Literal

from . import cbz, cir, epub, pdf

SupportedInputs = Literal["cbz", "epub", "pdf", "cir"]
OutputFn = Callable[[Path, Path], None]

INPUT_FN_MAP: dict[SupportedInputs, OutputFn] = {
    "cbz": cbz.create_cir,
    "epub": epub.create_cir,
    "pdf": pdf.create_cir,
    "cir": cir.create_cir,
}


def create_cir(path: Path | str, dest: Path | str, ext: SupportedInputs) -> None:
    """
    Create a CIR from the given path.
    """
    path = Path(path)
    dest = Path(dest)
    return INPUT_FN_MAP[ext](path, dest)
