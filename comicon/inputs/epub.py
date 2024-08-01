from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, cast

from ebooklib import epub

from .. import cirtools
from ..base import Chapter, Comic, Metadata

XML_NAMESPACE = "http://purl.org/dc/elements/1.1/"


def create_cir(path: Path, dest: Path) -> Iterator[str | int]:
    book = epub.read_epub(path)
    comic = create_metadata_from_comicon(book)
    book_metadata = create_metadata_from_book(book)
    if comic:
        comic.metadata.merge_with(book_metadata)
        return create_cir_from_comicon(dest, book, comic)
    return create_cir_from_other(dest, book, book_metadata)


def create_metadata_from_comicon(book: epub.EpubBook) -> Comic | None:
    """
    Search the book for a Comicon data file and attempt to parse its metadata.
    If no data file is found, return None.
    """
    out: list[epub.EpubItem] = list(book.get_items())
    for item in out:
        match item.file_name.split("/"):
            case ["static", cirtools.IR_DATA_FILE]:
                return Comic.from_json(item.get_content())
            case _:
                ...
    return None


def create_metadata_from_book(book: epub.EpubBook) -> Metadata:
    """
    Search for metadata in the book itself, returning a comic
    with the populated metadata but no chapters.
    """
    # look at TOC, take title and slug from each
    # look at spine, be like noveldown
    metadata = book.metadata[XML_NAMESPACE]
    title: str = metadata["title"][0][0]
    description: str = metadata["description"][0][0]
    authors: list[str] = [author for author, _ in metadata["creator"]]
    genres: list[str] = [genre for genre, _ in metadata["subject"]]

    cover_item_rel: str | None = None
    cover_item = get_cover_item(book)
    if cover_item:
        cover_item_rel = cover_item.file_name.split("/")[-1]

    return Metadata(title, authors, description, genres, cover_item_rel)


def get_cover_item(book: epub.EpubBook) -> epub.EpubItem | None:
    """
    Attempt to find the cover image item in the book.
    """
    try:
        imgdir = book.get_metadata("OPF", "cover")[0][1]["content"]
        cover_item: epub.EpubItem = book.get_item_with_id(imgdir)
        return cover_item
    except (KeyError, IndexError):
        # no cover image
        ...
    return None


def create_cir_from_comicon(dest: Path, book: epub.EpubBook, comic: Comic) -> Iterator[str | int]:
    # we can make a *lot* of assumptions
    (dest / cirtools.IR_DATA_FILE).write_text(comic.to_json())

    yield len(list(book.get_items()))
    for item in book.get_items():
        item = cast(epub.EpubItem, item)
        match item.file_name.split("/"):
            case ["img", slug, image_name]:
                # we can assume that the slug is the same as the chapter slug
                # but it might be good to check it anyway
                dest_path = dest / slug / image_name
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                yield str(dest_path)

                dest_path.write_bytes(item.get_content())
            case [comic.metadata.cover_path_rel] if comic.metadata.cover_path_rel:
                dest_path = dest / comic.metadata.cover_path_rel
                dest_path.write_bytes(item.get_content())
            case _:
                # ignore all other files because comicon.json has everything
                # we need
                pass


def create_cir_from_other(
    dest: Path, book: epub.EpubBook, metadata: Metadata
) -> Iterator[str | int]:
    if metadata.cover_path_rel:
        cover_path = dest / metadata.cover_path_rel
        # this must be true because cover_path_rel exists
        cover_item = cast(epub.EpubItem, get_cover_item(book))
        cover_path.write_bytes(cover_item.get_content())

    # assume that there can be no duplicate IDs in
    # a properly formed EPUB
    cache_dict: dict[str, epub.EpubItem] = {}

    for item in book.get_items():
        cache_dict[item.id] = item

    # list of tuples of chapter and list of hrefs
    chapters: list[tuple[ChapterPageMetadata, list[epub.EpubItem]]] = [
        (ChapterPageMetadata(Chapter(chap.title, chap.uid), chap.href), []) for chap in book.toc
    ]
    item = 0  # represents next chapter

    yield len(book.spine)  # num pages to copy
    for page, _ in book.spine:
        page: epub.EpubItem = book.get_item_with_id(page)
        full_path = str(("/" / Path(page.file_name)).resolve()).removeprefix(dest.anchor)

        if len(chapters) == item:
            # add anything after the last chapter
            chapters[-1][1].append(page)
        elif chapters[item][0].href.endswith(full_path):
            # next chapter
            item += 1
            chapters[item - 1][1].append(page)
        elif item > 0:
            # ignore anything before the first chapter
            # this is a hack so we don't have to create a new chapter
            chapters[item - 1][1].append(page)

    comic = Comic(metadata, [chapter.base_chap for chapter, _ in chapters])
    (dest / cirtools.IR_DATA_FILE).write_text(comic.to_json())

    for chapter, page_list in chapters:
        chapter_dir = dest / chapter.base_chap.slug
        chapter_dir.mkdir(exist_ok=True)
        # copy meta
        for i, page in enumerate(page_list, start=1):
            # TODO: allow for more than one image per XHTML / HTML file
            # beautiful soup?
            html_content = page.get_content().decode()
            ind_start = html_content.find('<img src="') + len('<img src="')
            if ind_start == len('<img src="') - 1:
                # not found
                continue
            ind_end = html_content.find('"', ind_start)
            img_href = Path(html_content[ind_start:ind_end])

            # because .parent normalises it
            cd = ("/" / Path(page.file_name)).parent

            drive_root = cd.anchor
            img_path_abs = str(
                # if in form ../img/blah and cd = /pages/test
                # then return pages/img/blah
                img_href if img_href.is_absolute() else (cd / img_href).resolve()
            ).removeprefix(drive_root)

            for item in book.get_items():
                if item.file_name == img_path_abs:
                    img_item = item
                    break
            else:
                # none found
                continue

            if img_item is not None:
                ext = Path(img_item.file_name).suffix
                page_path = chapter_dir / f"{i:05}{ext}"
                page_path.write_bytes(img_item.get_content())
                yield str(page_path)


@dataclass
class ChapterPageMetadata:
    base_chap: Chapter
    href: str

    def __post_init__(self) -> None:
        self.href = str(Path(self.href).resolve())
