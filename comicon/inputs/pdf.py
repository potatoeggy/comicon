import itertools
from pathlib import Path
from typing import Iterator

from pypdf import PdfReader

from .. import cirtools
from ..base import Chapter, Comic, Metadata


def create_cir(path: Path, dest: Path) -> Iterator[str | int]:
    """
    Create an IR folder from the given comic path.

    This function creates
    """

    reader = PdfReader(path)
    title = path.name
    if reader.metadata:
        if reader.metadata.title:
            title = reader.metadata.title

        author_str = reader.metadata.author
        authors = author_str.split(",") if author_str else []

        # PyPDF does not support getting keywords
        # genre_str = reader.documentInfo["/Keywords"]
        # genres = genre_str.split(",") if genre_str else []
        genres: list[str] = []
        description = reader.metadata.subject

        # det if this is a comicon comic
        # we can use the "extra_metadata": "pdf_pages" fields to
        # to check via duck typings
        inferred_metadata = Metadata(title, authors, description, genres, "")

        if reader.metadata.producer == "comicon":
            comic = Comic.from_json(reader.metadata.creator)
            comic.metadata.merge_with(inferred_metadata)
        else:
            comic = Comic(inferred_metadata, [Chapter("Chapter 1", "chapter-1")])
    else:
        empty_metadata = Metadata(title, [], "", [], "")
        comic = Comic(empty_metadata, [Chapter("Chapter 1", "chapter-1")])

        # use first image as cover
    yield len(reader.pages)

    # below is for OTHER only
    cover_name = ""  # guaranteed to be set in loop unless there are no images

    # this is gonna be real ugly
    i = 0  # chapter count
    page_iter = itertools.chain(*(p.images for p in reader.pages))

    # i will stop code golfing soon:tm:
    # this is a quick prototype to get it ready for mandown 1.3
    i = 1
    cur_chap = 0  # current chapter index
    chap_path = dest / comic.chapters[0].slug
    is_comicon_comic = reader.metadata.producer == "comicon"

    i = 0
    while (image := next(page_iter, None)) is not None:
        chap_path.mkdir(exist_ok=True)
        ext = image.name.split(".")[-1]

        if i == 0:
            i = 1
            cover_name = f"cover.{ext}"

            if not is_comicon_comic or comic.metadata.cover_path_rel:
                (dest / cover_name).write_bytes(image.data)
                comic.metadata.cover_path_rel = cover_name
                continue

        (chap_path / f"{i:05}.{ext}").write_bytes(image.data)
        yield str(chap_path)
        if is_comicon_comic:
            # if converting back from comicon
            cur_chap_page_limit = comic.metadata.extra_metadata["pdf_pages"][cur_chap]
            if cur_chap_page_limit == i and cur_chap < len(comic.chapters) - 1:
                i = 1
                cur_chap += 1
                chap_path = dest / comic.chapters[cur_chap].slug
                continue  # do not i += 1
        i += 1
    (dest / cirtools.IR_DATA_FILE).write_text(comic.to_json())
