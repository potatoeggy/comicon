from pathlib import Path
from typing import Callable, Iterator, Literal, get_args

from .. import cirtools
from . import cbz, cir, epub, mobi, pdf

SupportedOutputs = Literal["cbz", "epub", "pdf", "cir", "mobi"]
OutputFn = Callable[[Path, Path], Iterator[str | int]]

SupportedOutputList: tuple[SupportedOutputs] = get_args(SupportedOutputs)  # type: ignore

OUTPUT_FN_MAP: dict[SupportedOutputs, OutputFn] = {
    "cbz": cbz.create_comic,
    "epub": epub.create_comic,
    "pdf": pdf.create_comic,
    "cir": cir.create_comic,
    "mobi": mobi.create_comic,
}


def create_comic(
    ir_path: Path | str,
    dest: Path | str,
    ext: SupportedOutputs | None = None,
    validate: bool = True,
) -> None:
    for _ in create_comic_progress(ir_path, dest, ext, validate):
        ...


def create_comic_progress(
    ir_path: Path | str,
    dest: Path | str,
    ext: SupportedOutputs | None = None,
    validate: bool = True,
) -> Iterator[str | int]:
    # TODO: make iterator for progress bar
    """
    Create a comic from the given CIR path.

    :param `cir_path`: The path to the IR folder.
    :param `dest`: The path to the destination file.
    :param `ext`: An optional file extension string denoting the
    desired file extension.
    :param `validate`: Whether to validate the CIR before creation.
    """
    ir_path = Path(ir_path)
    dest = Path(dest)

    inferred_ext = dest.suffix.lower().split(".")[-1]
    if not ext and inferred_ext not in get_args(SupportedOutputs):
        raise ValueError(f"Could not infer a supported output extension ({inferred_ext})")

    if validate:
        cirtools.validate_cir(ir_path)

    if dest.is_dir():
        raise IsADirectoryError(
            f"{dest} is a directory. Make sure you pass the filepath to the new comic file."
        )
    yield from OUTPUT_FN_MAP[ext or inferred_ext](ir_path, dest)
