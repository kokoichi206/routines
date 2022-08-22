import abc
from typing import List

from entity.book import BookItem


class BookUploader(metaclass=abc.ABCMeta):
    """Class for uploading books' information."""

    # Class uploader must have fetch method
    @abc.abstractmethod
    def fetch(self) -> List[BookItem]:
        raise NotImplementedError()

    @abc.abstractmethod
    def upload(self, books: List[BookItem]) -> bool:
        raise NotImplementedError()
