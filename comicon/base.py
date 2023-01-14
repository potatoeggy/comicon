from dataclasses import dataclass, field


@dataclass
class BaseChapter:
    title: str
    slug: str  # on the filesystem


@dataclass
class BaseMetadata:
    title: str
    authors: list[str] = field(default_factory=list)
    description: str | None = None
    genres: list[str] = field(default_factory=list)
    extra_metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class BaseComic:
    metadata: BaseMetadata
    chapters: list[BaseChapter]
