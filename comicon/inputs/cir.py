from pathlib import Path


def create_cir(path: Path, dest: Path) -> None:
    path = path.resolve()
    dest = dest.resolve()

    if path == dest:
        # skip the copy if the source and destination are the same
        return
