import json
from dataclasses import asdict, dataclass, field


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
    cover_path_rel: str | None = None
    extra_metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class BaseComic:
    metadata: BaseMetadata
    chapters: list[BaseChapter]

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)
