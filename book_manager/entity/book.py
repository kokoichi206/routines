from dataclasses import dataclass, field
from typing import List

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(eq=False)
class BookItem:
    """Class for keeping track of books' information."""
    title: str
    url: str
    tags: List[str] = field(default_factory=list)

    def __eq__(self, other):

        if not isinstance(other, BookItem):
            return False
        return self.title == other.title and self.url == other.url
