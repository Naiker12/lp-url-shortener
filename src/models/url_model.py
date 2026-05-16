from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class UrlRecord:
    codigo: str
    url_original: str
    created_at: str
    clicks: int = 0

    def to_item(self) -> dict:
        return asdict(self)
