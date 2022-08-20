import abc
from typing import List

from entity.book import BookItem


class BookFetcher(metaclass=abc.ABCMeta):
    """Class for fetching books' information."""
    @abc.abstractmethod
    def fetch(self) -> List[BookItem]:
        raise NotImplementedError()
