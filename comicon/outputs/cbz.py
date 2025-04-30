import os
import zipfile
from pathlib import Path
from typing import Iterator

from lxml import etree
from lxml.builder import E

from .. import cirtools
from ..common.cbz import build_page_index


def create_comic(cir_path: Path, dest: Path) -> Iterator[str | int]:
    """
    Create a comic from the given IR path. Metadata is stored in ComicInfo.xml
    and `comicon.json`.
    """
    comic = cirtools.read_metadata(cir_path)
    page_index = build_page_index(cir_path, comic)

    tree = E.ComicInfo(
        E.Title(
            comic.metadata.title,
        ),
        E.Summary(comic.metadata.description),
        E.Writer(", ".join(comic.metadata.authors)),
        E.Genre(", ".join(comic.metadata.genres)),
        E.PageCount(str(len(page_index))),
        E.Pages(*[E.Page(**page.build_lxml_kwargs()) for page in page_index]),
        # TODO: add pages
    )
    text_xml = etree.tostring(
        tree, pretty_print=True, encoding="utf-8", xml_declaration=True
    ).decode()

    yield len(comic.chapters)  # chapter count

    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as file:
        for i, chap in enumerate(comic.chapters, start=1):
            chap_path = cir_path / chap.slug
            rel_chap_path = chap_path.with_name(f"{i:05}-{chap.slug}")
            for image in sorted(chap_path.iterdir()):
                new_img_path = rel_chap_path / image.name
                file.write(
                    image,
                    # we cannot use Path.relative_to here because it does not support making a path
                    # relative to another relative path if the first path is an absolute path
                    # https://stackoverflow.com/questions/67452690/pathlib-path-relative-to-vs-os-path-relpath
                    os.path.relpath(new_img_path.absolute(), cir_path),
                    zipfile.ZIP_DEFLATED,
                )
            yield str(i)

        if comic.metadata.cover_path_rel:
            cover_path = cir_path / comic.metadata.cover_path_rel
            file.write(
                cover_path,
                # rename cover to appear first in the archive
                os.path.relpath(cover_path.with_stem("..cover").absolute(), cir_path),
                zipfile.ZIP_DEFLATED,
            )
        file.writestr("ComicInfo.xml", text_xml)
        file.writestr(cirtools.IR_DATA_FILE, comic.to_json())
