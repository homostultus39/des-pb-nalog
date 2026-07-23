from dataclasses import dataclass, field


@dataclass
class SearchResult:
    success: bool
    error: str | None
    duration: float
    collect_time: str
    entities: list
    total: int = field(init=False)

    def __post_init__(self):
        self.total = len(self.entities)