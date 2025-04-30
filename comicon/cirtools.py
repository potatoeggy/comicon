"""
Tools for working with the Comicon Intermediate Representation (CIR).

The CIR is a folder that must contain the following:

- `comicon.json`: a JSON file containing the metadata for the comic (see `base.py`)
- `{chapter-slug}/`: folders where `chapter-slug` is the slugified chapter name as
defined in `comicon.json`
    - `{number}.{ext}`: ordered image files representing one comic page (min. 1)
- `cover.{ext}`: a file containing the cover of the comic. Extensions allowed include
jpg, jpeg, js2, png, gif, and webp.

All folders as well as the cover image must be declared in `comicon.json`. Only image
files are allowed in the chapter folders, but any file is allowed in the root of
the CIR folder.

Extra files or folders in the CIR root will be ignored.
"""

import json
from pathlib import Path

from .base import Comic
from .errors import (
    BadImageError,
    EmptyChapterError,
    NoChaptersError,
    UnusedChapterError,
)
from .image import ACCEPTED_IMAGE_EXTENSIONS

IR_DATA_FILE = "comicon.json"
ALLOWED_COVER_EXTENSIONS = ACCEPTED_IMAGE_EXTENSIONS


def read_metadata(path: Path | str) -> Comic:
    """
    Read metadata from a CIR folder.
    """
    path = Path(path)
    data_file = path / IR_DATA_FILE
    with open(data_file, "r", encoding="utf-8") as file:
        data = json.load(file)
        return Comic.from_json(data)


def validate_cir(path: Path | str) -> None:
    """
    Validate that the CIR folder is properly formed.
    """
    # this is our little unit test

    path = Path(path)
    if not path.is_dir():
        raise NotADirectoryError(f"{path} is not a directory")

    # check that comicon.json exists
    data_file = path / IR_DATA_FILE
    if not data_file.is_file():
        raise FileNotFoundError(f"{data_file} does not exist")

    # check that comicon.json follows base.Comic
    with open(data_file, "r", encoding="utf-8") as file:
        data = json.load(file)
        comic = Comic.from_json(data)

    # check at at least one chapter exists
    chapter_folders = sorted(f for f in path.iterdir() if f.is_dir())
    if not chapter_folders:
        raise NoChaptersError("No chapter folders found")

    # check that all chapter folders are declared in comicon.json
    chapter_slugs = {c.slug for c in comic.chapters}
    chapter_folder_set = {f.name for f in chapter_folders}
    if diff := chapter_slugs - chapter_folder_set:
        raise UnusedChapterError(
            f"Chapters were declared in {data_file} but were not found in the filesystem: {diff}"
        )

    # check that all chapter folders contain at least one image
    for chapter_folder in chapter_folders:
        images = sorted(f for f in chapter_folder.iterdir() if f.is_file())
        if not images:
            raise EmptyChapterError(f"{chapter_folder} is empty")
        for image in images:
            if image.suffix.lower() not in ALLOWED_COVER_EXTENSIONS:
                raise BadImageError(f"{image} is not an image")

    # check that the cover image exists
    if comic.metadata.cover_path_rel:
        cover_path = path / f"{comic.metadata.cover_path_rel}"
        if not cover_path.is_file():
            raise FileNotFoundError(f"{cover_path} does not exist but is declared in {data_file}")
        if cover_path.suffix.lower() not in ALLOWED_COVER_EXTENSIONS:
            raise BadImageError(f"{cover_path} is not an accepted image")


def count_pages(path: Path) -> int:
    """
    Count the number of pages in a comic.
    """
    comic = read_metadata(path)
    total = 0
    for chap in comic.chapters:
        total += len(list((path / chap.slug).iterdir()))
    return total
