from typing import List

from google.auth.transport.requests import AuthorizedSession
from google.oauth2.credentials import Credentials

from api.interface.book_fetcher import BookFetcher
from entity.book import BookItem


class DriveManager(BookFetcher):
    """Fetch file names and IDs from a Google Drive folder using OAuth."""

    def __init__(self, folder_id: str, credentials: Credentials, pdf_only: bool = True) -> None:
        self._folder_id = folder_id
        self._credentials = credentials
        self._pdf_only = pdf_only

    def fetch(self) -> List[BookItem]:
        books = []
        params = {
            "q": f"'{self._folder_id}' in parents and trashed = false and mimeType != 'application/vnd.google-apps.folder'",
            "fields": "files(id,name),nextPageToken",
            "pageSize": 1000,
        }
        with AuthorizedSession(self._credentials) as session:
            while True:
                response = session.get(
                    "https://www.googleapis.com/drive/v3/files",
                    params=params,
                    timeout=30,
                )
                response.raise_for_status()
                page = response.json()
                for file in page["files"]:
                    if not self._pdf_only or file["name"].endswith(".pdf"):
                        books.append(BookItem(
                            title=file["name"],
                            url=f"https://drive.google.com/file/d/{file['id']}/view?usp=sharing",
                        ))
                next_page_token = page.get("nextPageToken")
                if not next_page_token:
                    break
                params["pageToken"] = next_page_token
        return books
