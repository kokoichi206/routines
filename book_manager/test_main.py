from unittest.mock import Mock

import pytest

from entity.book import BookItem
from main import main


def test_main_uploads_only_missing_books_and_reads_them_back():
    old_book = BookItem("old.pdf", "https://example.com/old")
    new_book = BookItem("new.pdf", "https://example.com/new")
    fetcher = Mock()
    fetcher.fetch.return_value = [old_book, new_book]
    uploader = Mock()
    uploader.fetch.side_effect = [[old_book], [old_book, new_book]]

    counts = main(fetcher, uploader)

    uploader.upload.assert_called_once_with([new_book])
    assert uploader.fetch.call_count == 2
    assert counts == {"source": 2, "existing": 1, "to_upload": 1}


def test_main_dry_run_does_not_write():
    fetcher = Mock()
    fetcher.fetch.return_value = [BookItem("new.pdf", "https://example.com/new")]
    uploader = Mock()
    uploader.fetch.return_value = []

    assert main(fetcher, uploader, dry_run=True)["to_upload"] == 1

    uploader.upload.assert_not_called()
    uploader.fetch.assert_called_once()


def test_main_fails_if_uploaded_books_are_missing_on_readback():
    fetcher = Mock()
    fetcher.fetch.return_value = [BookItem("new.pdf", "https://example.com/new")]
    uploader = Mock()
    uploader.fetch.side_effect = [[], []]

    with pytest.raises(RuntimeError, match="Notion is missing 1 source items"):
        main(fetcher, uploader)
