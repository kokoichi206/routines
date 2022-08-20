from dataclasses import dataclass


@dataclass
class BookItem:
    """Class for keeping track of books' information."""
    title: str
    url: str
    tags: list[str]
