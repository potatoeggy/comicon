import json
from dataclasses import asdict, dataclass, field
from typing import Any, cast

from slugify import slugify

SLUGIFY_ARGS = {
    "allow_unicode": True,
    "regex_pattern": r'["<:\?\*\|/>\\]+',
    "replacements": [
        [":", ";"],
        ["/", ""],
        ["?", ""],
        ["*", "x"],
        ["|", ""],
        ["<", ""],
        [">", ""],
        ['"', ""],
        ["!", ""],
        ["'", "`"],
    ],
    "lowercase": False,
}


@dataclass
class Chapter:
    title: str
    slug: str  # on the filesystem


@dataclass
class Metadata:
    title: str
    authors: list[str] = field(default_factory=list)
    description: str | None = None
    genres: list[str] = field(default_factory=list)
    cover_path_rel: str | None = None
    extra_metadata: dict[str, Any] = field(default_factory=dict)
    title_slug: str = ""

    def __post_init__(self):
        self.title_slug = slugify(self.title, **SLUGIFY_ARGS)

    def merge_with(self, other: "Metadata") -> "Metadata":
        """
        Merge metadata from two comics. The new comic's metadata takes precedence,
        as long as it exists. This updates the current metadata in place.
        """
        if other.title:
            self.title = other.title

        if other.authors:
            self.authors = other.authors

        if other.description:
            self.description = other.description

        if other.genres:
            self.genres = other.genres

        if other.cover_path_rel:
            self.cover_path_rel = other.cover_path_rel

        if other.extra_metadata:
            self.extra_metadata = self.extra_metadata | other.extra_metadata

        return self


@dataclass
class Comic:
    metadata: Metadata
    chapters: list[Chapter]

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_json(cls, dict_str: str | bytes | dict) -> "Comic":
        if not isinstance(dict_str, dict):
            dict_str = json.loads(dict_str)

        dict_str = cast(dict, dict_str)
        return cls(
            Metadata(**dict_str["metadata"]),
            [Chapter(**c) for c in dict_str["chapters"]],
        )
