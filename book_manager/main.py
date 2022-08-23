import datetime
import json
import os
from typing import List

from api.impl.drive_manager import DriveManager
from api.impl.notion_manager import NotionManager
from api.interface.book_fetcher import BookFetcher
from api.interface.book_uploader import BookUploader
from config.setup import load_google_drive_config, load_notion_config
from entity.book import BookItem


def main(fetcher: BookFetcher, uploader: BookUploader) -> None:
    """Upload only un-uploaded BookItems.

    Args:
        book fetcher (:class:`BookFetcher`): Book fetcher.
        book uploader (:class:`BookUploader`): Book uploader.
    """

    new_books = fetcher.fetch()
    old_books = uploader.fetch()
    to_upload: List[BookItem] = []
    for book in new_books:
        # If the book is already uploaded, skip uploading.
        if book in old_books:
            continue
        to_upload.append(book)
    if uploader.upload(to_upload):
        print(f"Succsessfully uploaded {len(to_upload)} items.")
    else:
        print(f"Failed to upload {len(to_upload)} items.")


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
    drive_fetcher = DriveManager(
        url=drive_config.url,
    )

    ## DI
    main(drive_fetcher, notion)

    ## Other examples
    # dump_json(notion)
    # load_book_items(os.path.join("data", "books_2022_0823_0350.json"))
