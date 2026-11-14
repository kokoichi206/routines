import datetime
import json
import os
from typing import Dict, List

from google.oauth2.credentials import Credentials

from api.impl.drive_manager import DriveManager
from api.impl.notion_manager import NotionManager
from api.interface.book_fetcher import BookFetcher
from api.interface.book_uploader import BookUploader
from config.setup import load_google_drive_config, load_notion_config
from entity.book import BookItem


def main(fetcher: BookFetcher, uploader: BookUploader, dry_run: bool = False) -> Dict[str, int]:
    """Upload only un-uploaded BookItems.

    Args:
        book fetcher (:class:`BookFetcher`): Book fetcher.
        book uploader (:class:`BookUploader`): Book uploader.
    """

    new_books = fetcher.fetch()
    old_books = uploader.fetch()
    registered_urls = {book.url for book in old_books}
    to_upload: List[BookItem] = []
    for book in new_books:
        # Preserve titles edited in Notion when the Drive file is already registered.
        if book.url in registered_urls:
            continue
        to_upload.append(book)
    counts = {"source": len(new_books), "existing": len(new_books) - len(to_upload), "to_upload": len(to_upload)}
    if dry_run:
        return counts
    if not uploader.upload(to_upload):
        raise RuntimeError(f"Failed to upload {len(to_upload)} items.")
    registered_books = uploader.fetch()
    registered_urls = {book.url for book in registered_books}
    missing_books = [book for book in new_books if book.url not in registered_urls]
    if missing_books:
        raise RuntimeError(f"Notion is missing {len(missing_books)} source items after upload: {[(book.title, book.url) for book in missing_books]}")
    print(f"Successfully uploaded {len(to_upload)} items and verified {len(new_books)} items.")
    return counts


def dump_json(fetcher: BookFetcher) -> None:
    """Fetch BookItems and save them as a json file.

    Args:
        book fetcher (:class:`BookFetcher`): Book fetcher.
    """

    books = fetcher.fetch()

    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(JST)

    date = now.strftime("%Y_%m%d_%H%M")
    path = os.path.join("data", f"books_{date}.json")
    with open(path, mode='w') as f:
        f.write(json.dumps(
            [book.to_json(indent=4, ensure_ascii=False) for book in books],
            indent=4, ensure_ascii=False))


def load_book_items(path: str) -> List[BookItem]:
    """Fetch BookItems and save them as a json file.

    Args:
        path (str): Path to dumped json file.

    Returns:
        formatted date (List[:class:`BookItem`]): Data about books.
    """

    with open(path) as f:
        df = json.load(f)
    return [BookItem.from_json(d) for d in df]


if __name__ == '__main__':

    notion_config = load_notion_config()
    notion = NotionManager(
        api_key=notion_config.api_key,
        database_id=notion_config.database_id,
    )

    drive_config = load_google_drive_config()
    drive_credentials = Credentials.from_authorized_user_info(
        json.loads(os.environ["GOOGLE_DRIVE_OAUTH_JSON"]),
    )
    folder_ids = [drive_config.folder_id] + os.getenv("ONE_TIME_DRIVE_FOLDER_IDS", "").split()
    dry_run = os.getenv("BOOK_MANAGER_DRY_RUN") == "true"
    for index, folder_id in enumerate(folder_ids):
        drive_fetcher = DriveManager(
            folder_id=folder_id,
            credentials=drive_credentials,
            pdf_only=index == 0,
        )
        counts = main(drive_fetcher, notion, dry_run=dry_run)
        print(json.dumps({"mode": "scheduled_pdf" if index == 0 else "one_time_all_files",
                          "folder_id": folder_id, "dry_run": dry_run, **counts}))

    ## Other examples
    # dump_json(notion)
    # load_book_items(os.path.join("data", "books_2022_0823_0350.json"))
