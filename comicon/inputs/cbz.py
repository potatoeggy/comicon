# support ComicInfo.xml
import zipfile
from pathlib import Path

from ..cirtools import IR_DATA_FILE


def create_cir(path: Path, dest: Path) -> None:
    """
    Convert a comic to the CIR format. Not all metadata can be converted,
    unless the comic was created by comicon.
    """
    with zipfile.ZipFile(path, "r", zipfile.ZIP_DEFLATED) as file:
        for name in file.namelist():
            if name.endswith("ComicInfo.xml"):
                ...
                # attempt to decode
            elif name.endswith(IR_DATA_FILE):
                ...
                # take metadata directly, overriding ComicInfo
            else:
                ...
                # the only other files should be images


# difficulties converting to CIR:
# - ensure that only images are copied from image folders
# - read comicinfo.xml
#
