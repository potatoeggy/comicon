# support ComicInfo.xml
from pathlib import Path


def create_cir(path: Path, dest: Path) -> None:
    raise NotImplementedError


# difficulties converting to CIR:
# - ensure that only images are copied from image folders
# - read comicinfo.xml
#
