from dataclasses import dataclass, field
from typing import List


@dataclass
class BookItem:
    """Class for keeping track of books' information."""
    title: str
    url: str
    tags: List[str] = field(default_factory=list)
