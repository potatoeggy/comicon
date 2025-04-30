# for metadata to check if there is a difference between
# comicon data and the one in the comicinfo.xml
# NOTE: THERE IS NO AUTHORITATIVE METADATA SOURCE
# comicon.json cannot be assumed to be correct
# we have to merge the two sources of metadata
# if they differ, defer to comicinfo.xml
#
# re chapters: if there is a difference in chapter count,
# defer to comicinfo.xml
# otherwise, defer to comicon.json

from dataclasses import dataclass
from pathlib import Path

from ..base import Comic
from ..image import WITH_WEBP_ACCEPTED_IMAGE_EXTENSIONS


@dataclass(kw_only=True)
class ComicInfoPageIndex:
    image: str  # page number
    image_size: str | None = None  # bytes
    image_height: str | None = None  # px
    image_width: str | None = None
    bookmark: str | None = None

    def build_lxml_kwargs(self) -> dict[str, str | None]:
        """
        Remove None values from the dictionary.
        """
        return {k: v for k, v in self.__dict__.items() if v is not None}


def build_page_index(cir_path: Path, comic: Comic) -> list[ComicInfoPageIndex]:
    """
    Build a page index for the comic. This is used to create the ComicInfo.xml file.
    """
    page_index = []

    i = 1
    for chap in comic.chapters:
        chap_path = cir_path / chap.slug
        for image_num, image in enumerate(sorted(chap_path.iterdir())):
            if image.suffix.lower() not in WITH_WEBP_ACCEPTED_IMAGE_EXTENSIONS:
                continue
            page_index.append(
                ComicInfoPageIndex(
                    image=str(i),
                    image_size=str(image.stat().st_size),
                    bookmark=chap.title if image_num == 0 else None,
                )
            )
            i += 1

    return page_index
