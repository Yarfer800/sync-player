from dataclasses import dataclass
from typing import Optional

@dataclass
class SearchResult:
    url: str
    title: str
    description: str
    thumbnail: Optional[str] = None
