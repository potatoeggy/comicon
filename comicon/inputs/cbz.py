# support ComicInfo.xml
import json
import zipfile
from pathlib import Path
from typing import Iterator, TypedDict

from lxml import etree
from slugify import slugify

from ..base import Chapter, Comic, Metadata, SLUGIFY_ARGS
from ..cirtools import IR_DATA_FILE
from ..image import ACCEPTED_IMAGE_EXTENSIONS

class MetadataDict(TypedDict):
    title: str
    authors: list[str]
    description: str
    genres: list[str]
    cover_path_rel: str
    extra_metadata: dict[str, str]


def create_cir(path: Path, dest: Path) -> Iterator[str | int]:
    """
    Convert a comic to the CIR format. Not all metadata can be converted,
    unless the comic was created by comicon.
    """

    data_dict: MetadataDict = {
        # mypy made me populate - consider switching to dataclass
        "title": "",
        "authors": [],
        "description": "",
        "genres": [],
        "cover_path_rel": "",
        "extra_metadata": {},
    }

    chapters = []
    chapter_index = {}
    found_comicon_metadata = False
    image_paths: list[Path] = []
    with zipfile.ZipFile(path, "r", zipfile.ZIP_DEFLATED) as z:
        for name in z.namelist():
            if name.endswith("ComicInfo.xml"):
                with z.open(name) as file:
                    maintree = etree.parse(file)

                for el in maintree.iter():
                    match el.tag:
                        case "Title":
                            data_dict["title"] = str(el.text)
                        case "Summary":
                            data_dict["description"] = str(el.text)
                        case "Writer":
                            data_dict["authors"] = str(el.text).split(", ")
                        case "Genre":
                            data_dict["genres"] = str(el.text).split(", ")
                    if el.tag == "Pages":
                        for page in el.iter():
                            if page.tag == "Page" and "Image" in page.attrib:
                                if "Bookmark" in page.attrib:
                                    chapters.append(Chapter(page.attrib["Bookmark"], slugify(page.attrib["Bookmark"], **SLUGIFY_ARGS)))
                                    chapter_index[page.attrib["Bookmark"]] = int(page.attrib["Image"])
                                elif "Type" in page.attrib:
                                    chapters.append(Chapter(page.attrib["Type"], slugify(page.attrib["Type"], **SLUGIFY_ARGS)))
                                    chapter_index[page.attrib["Type"]] = int(page.attrib["Image"])
            elif name.endswith(IR_DATA_FILE):
                with z.open(name) as file:
                    data = file.read()

                comic = Comic.from_json(data)
                # TODO: guarantee that this is done last after we've looked
                # at all other possible sources of metadata
                comic.metadata.merge_with(Metadata(**data_dict))

                found_comicon_metadata = True
                break
            elif "cover" in name and Path(name).suffix in ACCEPTED_IMAGE_EXTENSIONS:
                # assume that any *cover*.{img} is the cover image
                # TODO: CAN AND WILL BREAK ON FOLDER NAMES
                data_dict["cover_path_rel"] = name
            elif (path := Path(name)).suffix in ACCEPTED_IMAGE_EXTENSIONS:
                # the only other files should be images
                # if it's comicon-created, we should be able to take the folder
                # structure and strip the leading chars, splitting at first "-"
                #
                # if it's not comicon-created, then we should just assume that
                # it's a single chapter
                image_paths.append(path)
            else:
                # ignore all other file types
                ...
        else:
            if not chapters:
                # TODO: remove hardcoded "chapter-1" and make it variable
                chapters.append(Chapter("Chapter 1", "chapter-1"))
                chapter_index["Chapter 1"] = 0
            comic = Comic(Metadata(**data_dict), chapters)

        with open(dest / IR_DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(comic.to_dict(), file, indent=2)

        if comic.metadata.cover_path_rel:
            # use data_dict instead of comic.metadata because it's more reliable
            with z.open(data_dict["cover_path_rel"]) as file:
                data = file.read()

            with open(dest / comic.metadata.cover_path_rel, "wb") as file:
                file.write(data)

        yield len(image_paths)

        if found_comicon_metadata:
            # directly copy all images to respective destination folders in CIR
            for image_path in image_paths:
                with z.open(str(image_path)) as file:
                    data = file.read()

                # strip the 00001- from the beginning of the path
                folder_slug = str(image_path).split("/")[0].split("-", maxsplit=1)[1]
                filename = Path(image_path).name
                new_path = dest / folder_slug
                new_path.mkdir(parents=True, exist_ok=True)
                with open(new_path / filename, "wb") as file:
                    file.write(data)
                    yield str(filename)
        else:
            # create chapters from the ComicInfo.xml Metadata or put them into a single folder if none are given
            image_paths = sorted(image_paths)
            chapters = sorted(chapters, key=lambda c: chapter_index[c.title])
            chapters.append(Chapter("END", "end"))
            chapter_index["END"] = len(image_paths)
            for i, chapter in enumerate(chapters[:-1]):
                (dest / chapter.slug).mkdir(exist_ok=True)

                start_page = chapter_index[chapter.title]
                end_page = chapter_index[chapters[i + 1].title]

                for j, image_path in enumerate(image_paths[start_page:end_page], start=1):
                    with z.open(str(image_path)) as file:
                        data = file.read()

                    ext = Path(image_path).suffix
                    new_path = dest / chapter.slug / f"{j:05}{ext}"
                    with open(new_path, "wb") as file:
                        file.write(data)
                        yield str(new_path)
