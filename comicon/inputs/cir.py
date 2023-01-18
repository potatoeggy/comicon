import shutil
from pathlib import Path
from typing import Iterator

from .. import cirtools


def create_cir(path: Path, dest: Path) -> Iterator[str | int]:
    path = path.resolve()
    dest = dest.resolve()

    # validate cir
    cirtools.validate_cir(path)

    if path == dest:
        # skip the copy if the source and destination are the same
        raise StopIteration

    files = list(path.iterdir())

    yield len(files)

    for root in files:
        if root.is_dir():
            shutil.copytree(root, dest / root.name)
        else:
            shutil.copyfile(root, dest / root.name)
        yield str(root.name)
