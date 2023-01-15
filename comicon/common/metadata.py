from dataclasses import dataclass
from pathlib import Path

from ..base import BaseMetadata


@dataclass(slots=True)
class ComicInfoXml:
    # check how calibre does it
    # there's ComicInfo.xml and zip file comments
    content: BaseMetadata

    @classmethod
    def from_file(cls, path: Path) -> "ComicInfoXml":
        """
        Read metadata from a ComicInfo.xml file
        """
        pass

    def to_file(self, path: Path):
        """
        Write metadata to a ComicInfo.xml file
        """
        pass
