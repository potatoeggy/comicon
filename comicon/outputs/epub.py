from pathlib import Path
from typing import Iterator

from ebooklib import epub

from .. import cirtools
from ..base import Chapter
from ..image import WITH_WEBP_EXTENSION_MIME_MAP

STYLE_CSS = """
@page {
    margin: 0
}

body {
    display: block;
    margin: 0;
    padding: 0;
}
""".strip()

PAGE_CONTENT_TEMPLATE = """<html>
  <head>
    <link rel="stylesheet" type="text/css" href="static/style.css"/>
  </head>

  <body>
    <img src="../{}"/>
  </body>
</html>
"""


def create_comic(cir_path: Path, dest: Path) -> Iterator[str | int]:
    comic = cirtools.read_metadata(cir_path)

    book = epub.EpubBook()
    book.set_language("en")
    book.set_title(comic.metadata.title)
    book.add_metadata("DC", "description", comic.metadata.description)

    for genre in comic.metadata.genres:
        book.add_metadata("DC", "subject", genre)

    if comic.metadata.cover_path_rel:
        cover_path = cir_path / comic.metadata.cover_path_rel
        cover_content = cover_path.read_bytes()
        cover_ext = cover_path.suffix.lower().strip(".")
        book.set_cover(f"cover.{cover_ext}", cover_content)

    for author in comic.metadata.authors:
        book.add_author(author)

    chapter_htmls: list[tuple[Chapter, list[epub.EpubHtml]]] = []

    yield len(comic.chapters)
    for j, chapter in enumerate(comic.chapters):
        chapter_htmls.append((chapter, []))
        chapter_path = cir_path / chapter.slug
        images = sorted(f for f in chapter_path.iterdir() if f.is_file())
        for i, image in enumerate(images):
            image_content = image.read_bytes()
            img = epub.EpubImage(  # pylint: disable=unexpected-keyword-arg
                uid=f"{chapter.slug}-{image.name}",
                file_name=f"img/{chapter.slug}/{image.name}",
                media_type=WITH_WEBP_EXTENSION_MIME_MAP[image.suffix.lower()],
                content=image_content,
            )

            page = epub.EpubHtml(
                uid=f"chap{j}-{i}",
                title=chapter.title,
                file_name=f"pages/{chapter.slug}-{i}.xhtml",
                content=PAGE_CONTENT_TEMPLATE.format(img.file_name),
            )

            book.add_item(img)
            book.add_item(page)
            chapter_htmls[-1][1].append(page)  # push to the latest chapter
        yield chapter.title

    book.toc = tuple(
        epub.Link(pages[0].file_name, chapter.title, chapter.slug)
        for chapter, pages in chapter_htmls
    )

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    nav_css = epub.EpubItem(
        uid="style_nav",
        file_name="static/style.css",
        media_type="text/css",
        content=STYLE_CSS,
    )
    book.add_item(nav_css)

    data_json = epub.EpubItem(
        uid="data_json",
        file_name=f"static/{cirtools.IR_DATA_FILE}",
        media_type="application/json",
        content=comic.to_json(),
    )
    book.add_item(data_json)

    book.spine = [*sum((pages for _, pages in chapter_htmls), [])]

    epub.write_epub(dest, book, {})
