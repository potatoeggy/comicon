import subprocess
from pathlib import Path
from typing import Iterator

from . import epub

KINDLEGEN_BIN = "kindlegen"


def check_kindlegen() -> None:
    # check if kindlegen is installed
    try:
        kindlegen_return_code = subprocess.run(
            [KINDLEGEN_BIN, "-locale", "en"],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        ).returncode
    except FileNotFoundError as err:
        raise RuntimeError(
            "Kindlegen was not found in the current PATH and is required for MOBI conversion."
        ) from err

    if kindlegen_return_code != 0:
        raise RuntimeError(
            f"Kindlegen failed with return code {kindlegen_return_code}. Is Kindlegen installed?"
        )


def create_comic(cir_path: Path, dest: Path) -> Iterator[str | int]:
    check_kindlegen()
    epub_dest = dest.with_suffix(".epub")
    yield from epub.create_comic(cir_path, epub_dest)

    output = subprocess.run(
        [
            KINDLEGEN_BIN,
            "-locale",
            "en",
            "-dont_append_source",
            epub_dest.resolve().absolute(),
        ],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    # attrib: https://github.com/ciromattia/kcc/../comic2ebook.py
    # under the ISC license
    try:
        for line in output.stdout.decode("utf-8").split("\n"):
            if "Error(" in line:
                raise RuntimeError(f"Kindlegen: {line}")
            elif ":E23026" in line:
                raise RuntimeError(
                    f"Kindlegen: EPUB file too big, please file a GitHub issue! {line}"
                )
            elif "I1036: Mobi file built successfully" in line:
                break
    except Exception as err:
        # unknown kindlegen error
        raise RuntimeError(f"Kindlegen: {output.stdout.decode('utf-8')}") from err

    epub_dest.unlink(missing_ok=True)
