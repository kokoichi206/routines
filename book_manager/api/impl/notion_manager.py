import json
from http import HTTPStatus
from typing import Dict, List

import requests

from api.interface.book_fetcher import BookFetcher
from api.interface.book_uploader import BookUploader
from entity.book import BookItem


class NotionManager(BookFetcher, BookUploader):
    """Class for fetching from and uploading to Notion."""

    def __init__(self, api_key: str, database_id: str):
        """Initialize instance variables.

        Args:
            api_key (str): Notion API key.
            database_id (str): Database id.
        """

        self.notion_api_key = api_key
        self.database_id = database_id
        self.headers = {"Authorization": f"Bearer {self.notion_api_key}",
                        "Content-Type": "application/json",
                        "Notion-Version": "2021-05-13"}

    def fetch(self) -> List[BookItem]:
        """Fetch pdf data from Notion database.

        Documentation: https://developers.notion.com/reference/post-database-query

        Returns:
            formatted date (List[:class:`BookItem`]): Data about books.
        """

        response = requests.request("POST",
                                    url=self._get_request_url(
                                        f"databases/{self.database_id}/query"),
                                    headers=self.headers)
        results = response.json()["results"]

        book_items = []
        for result in results:
            props = result.get("properties")

            title_props = props.get("title", {}).get("title", [])
            # If title is undefined @Notion, [] will be returned.
            if len(title_props) == 1:
                title = title_props[0].get("text", {}).get("content")

            url = props.get("url", {}).get("url")

            tag_props = props.get("tag", {}).get("rich_text", {})
            tags = []
            for tag in tag_props:
                tags.append(tag.get("text").get("content"))

            # If both url and title are set, append book information.
            if url and title:
                book_items.append(
                    BookItem(
                        title=title,
                        url=url,
                        tags=tags,
                    )
                )

        return book_items

    def upload(self, books: List[BookItem]) -> bool:
        """Upload pdf data to Notion database.

        Args:
            books' information (List[:class:`BookItem`]): Book information.

        Returns:
            result (bool): Whether uploads were successful or not.
        """

        result = True
        for book in books:
            result &= self._upload_book(book=book)

        return result

    def _upload_book(self, book: BookItem) -> bool:
        """Upload one book to Notion database.

        Documentation: https://developers.notion.com/reference/post-page

        Args:
            book information (:class:`BookItem`): Book information.

        Returns:
            result (bool): Whether a upload was successful or not.
        """

        body = self._make_request_body(book=book)
        response = requests.request("POST",
                                    url=self._get_request_url("pages"),
                                    headers=self.headers, data=json.dumps(body))

        return response.status_code == 200

    def _make_request_body(self, book: BookItem) -> Dict[str, any]:
        """Make request body for post a page.

        Args:
            book information (:class:`BookItem`): Book information.

        Returns:
            Dictionary for request body (Dict[str, any]): Request body for POST api.
        """

        properties = {}

        title = {
            "title": [{
                "text": {
                    "content": book.title
                }
            }]
        }
        properties["title"] = title
        url = {
            "url": book.url
        }
        properties["url"] = url
        tags = {
            "rich_text": [{
                "text": {
                    "content": ",".join(book.tags)
                }
            }]
        }
        properties["tag"] = tags

        body = {
            "parent": {
                "database_id": self.database_id
            },
            "properties": properties
        }
        return body

    def _get_request_url(self, end_point: str) -> str:
        """Get complete URL.

        Args:
            end_point (str): endpoint of the request.

        Returns:
            URL (str): URL from which manager will fetch pdf data.
        """

        return f"https://api.notion.com/v1/{end_point}"

    def db_connection_check(self) -> bool:
        """Connetion check whether the database_id and api_key are correct.

        Returns:
            result (bool): whether the database access is possible.
        """

        response = requests.request("GET",
                                    url=self._get_request_url(
                                        f"databases/{self.database_id}"),
                                    headers=self.headers)
        return HTTPStatus.OK.__eq__(response.status_code)
