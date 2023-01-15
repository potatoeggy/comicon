from pathlib import Path


def create_comic(cir_path: Path, dest: Path) -> None:
    ir_path = cir_path.resolve()
    dest = dest.resolve()

    if ir_path == dest:
        # skip the copy if the source and destination are the same
        return
