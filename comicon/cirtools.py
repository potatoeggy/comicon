"""
Tools for working with the Comicon Intermediate Representation (CIR).

The CIR is a folder that must contain the following:

- `comicon.json`: a JSON file containing the metadata for the comic (see `base.py`)
- `{chapter-slug}/`: folders where `chapter-slug` is the slugified chapter name as
defined in `comicon.json`
    - `{number}.{ext}`: ordered image files representing one comic page (min. 1)
- `cover.{ext}`: a file containing the cover of the comic. Extensions allowed include
jpg, jpeg, png, and gif.

All folders as well as the cover image must be declared in `comicon.json`. Only image
files are allowed in the chapter folders, but any file is allowed in the root of
the CIR folder.
"""

import json
from pathlib import Path

from .base import BaseChapter, BaseComic, BaseMetadata
from .errors import (
    BadImageError,
    EmptyChapterError,
    NoChaptersError,
    UnusedChapterError,
)

IR_DATA_FILE = "comicon.json"
ALLOWED_COVER_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif"]


def read_metadata(path: Path | str) -> BaseComic:
    """
    Read metadata from a CIR folder.
    """
    path = Path(path)
    data_file = path / IR_DATA_FILE
    with open(data_file, "r", encoding="utf-8") as file:
        data = json.load(file)
        return BaseComic(
            BaseMetadata(**data["metadata"]),
            [BaseChapter(**c) for c in data["chapters"]],
        )


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

    # check that comicon.json follows base.BaseComic
    with open(data_file, "r", encoding="utf-8") as file:
        data = json.load(file)
        comic = BaseComic(
            BaseMetadata(**data["metadata"]),
            [BaseChapter(**c) for c in data["chapters"]],
        )

    # check at at least one chapter exists
    chapter_folders = sorted(f for f in path.iterdir() if f.is_dir())
    if not chapter_folders:
        raise NoChaptersError("No chapter folders found")

    # check that all chapter folders are declared in comicon.json
    chapter_slugs = {c.slug for c in comic.chapters}
    for chapter_folder in chapter_folders:
        if chapter_folder.name not in chapter_slugs:
            raise UnusedChapterError(f"{chapter_folder} not declared in {data_file}")

    # check that all chapter folders contain at least one image
    for chapter_folder in chapter_folders:
        images = sorted(f for f in chapter_folder.iterdir() if f.is_file())
        if not images:
            raise EmptyChapterError(f"{chapter_folder} is empty")
        for image in images:
            if not image.suffix.lower() in ALLOWED_COVER_EXTENSIONS:
                raise BadImageError(f"{image} is not an image")

    # check that the cover image exists
    if comic.metadata.cover_path_rel:
        cover_path = path / f"{comic.metadata.cover_path_rel}"
        if not cover_path.is_file():
            raise FileNotFoundError(
                f"{cover_path} does not exist but is declared in {data_file}"
            )
        if not cover_path.suffix.lower() in ALLOWED_COVER_EXTENSIONS:
            raise BadImageError(f"{cover_path} is not an accepted image")
