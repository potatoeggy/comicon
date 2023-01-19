import json
from dataclasses import asdict, dataclass, field
from typing import Any


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


@dataclass
class Comic:
    metadata: Metadata
    chapters: list[Chapter]

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_json(cls, json_str: str | bytes) -> "Comic":
        data: dict = json.loads(json_str)
        return cls(
            Metadata(**data["metadata"]),
            [Chapter(**c) for c in data["chapters"]],
        )
