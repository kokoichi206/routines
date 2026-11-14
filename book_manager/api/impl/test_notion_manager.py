from unittest.mock import patch

import pytest
from requests import HTTPError

from api.impl.notion_manager import NotionManager
from entity.book import BookItem


def test_extract_book_data_skips_empty_title_and_joins_title_fragments():
    notion = NotionManager("test-key", "test-database")
    results = [
        {"properties": {"title": {"title": [{"plain_text": "first"}]}, "url": {"url": "url-1"}}},
        {"properties": {"title": {"title": []}, "url": {"url": "url-2"}}},
        {"properties": {"title": {"title": [{"plain_text": "second"}, {"plain_text": ".pdf"}]}, "url": {"url": "url-3"}}},
    ]

    assert notion._extract_book_data(results) == [BookItem("first", "url-1"), BookItem("second.pdf", "url-3")]


@patch("api.impl.notion_manager.requests.Session")
def test_notion_fetch_propagates_http_errors(session_class):
    session_class.return_value.request.return_value.raise_for_status.side_effect = HTTPError("401 Unauthorized")

    with pytest.raises(HTTPError, match="401 Unauthorized"):
        NotionManager("test-key", "test-database").fetch()
