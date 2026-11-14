from unittest.mock import Mock, patch

import pytest
from requests import HTTPError

from api.impl.drive_manager import DriveManager
from entity.book import BookItem


@patch("api.impl.drive_manager.AuthorizedSession")
def test_fetch_follows_pagination_and_preserves_book_identity(authorized_session):
    first_page = Mock()
    first_page.json.return_value = {
        "files": [
            {"id": "pdf-1", "name": "本.pdf"},
            {"id": "text-1", "name": "notes.txt"},
        ],
        "nextPageToken": "page-2",
    }
    empty_page = Mock()
    empty_page.json.return_value = {"files": [], "nextPageToken": "page-3"}
    last_page = Mock()
    last_page.json.return_value = {"files": [{"id": "pdf-2", "name": "another.pdf"}]}
    session = authorized_session.return_value.__enter__.return_value
    requested_params = []

    def get_page(url, *, params, timeout):
        requested_params.append(params.copy())
        return [first_page, empty_page, last_page][len(requested_params) - 1]

    session.get.side_effect = get_page
    credentials = Mock()

    books = DriveManager("folder-id", credentials).fetch()

    assert books == [
        BookItem("本.pdf", "https://drive.google.com/file/d/pdf-1/view?usp=sharing"),
        BookItem("another.pdf", "https://drive.google.com/file/d/pdf-2/view?usp=sharing"),
    ]
    assert "pageToken" not in requested_params[0]
    assert requested_params[1]["pageToken"] == "page-2"
    assert requested_params[2]["pageToken"] == "page-3"
    assert all(params["q"] == "'folder-id' in parents and trashed = false and mimeType != 'application/vnd.google-apps.folder'" for params in requested_params)
    for page in (first_page, empty_page, last_page):
        page.raise_for_status.assert_called_once()


@patch("api.impl.drive_manager.AuthorizedSession")
def test_fetch_propagates_drive_api_errors(authorized_session):
    session = authorized_session.return_value.__enter__.return_value
    session.get.return_value.raise_for_status.side_effect = HTTPError("403 Forbidden")

    with pytest.raises(HTTPError, match="403 Forbidden"):
        DriveManager("folder-id", Mock()).fetch()

    session.get.return_value.json.assert_not_called()


@patch("api.impl.drive_manager.AuthorizedSession")
def test_fetch_all_files_includes_names_without_pdf_extension(authorized_session):
    session = authorized_session.return_value.__enter__.return_value
    session.get.return_value.json.return_value = {
        "files": [{"id": "pdf-1", "name": "book.pdf"}, {"id": "file-2", "name": "README.md"}],
    }

    books = DriveManager("folder-id", Mock(), pdf_only=False).fetch()

    assert [book.title for book in books] == ["book.pdf", "README.md"]
