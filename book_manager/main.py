from api.impl.drive_manager import DriveManager
from api.impl.notion_manager import NotionManager
from api.interface.book_fetcher import BookFetcher
from api.interface.book_uploader import BookUploader
from config.setup import load_google_drive_config, load_notion_config


def main(fetcher: BookFetcher, uploader: BookUploader) -> None:
    books = fetcher.fetch()
    for book in books:
        print(book)
    print(f"Fetched data length: {len(books)}")


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

    # DI
    main(
        fetcher=drive_fetcher,
        uploader=notion,
    )
