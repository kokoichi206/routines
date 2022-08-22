from api.impl.drive_manager import DriveManager
from api.interface.book_fetcher import BookFetcher
from api.interface.book_uploader import BookUploader
from entity.book import BookItem


def main(fetcher: BookFetcher, uploader: BookUploader) -> None:
    books = fetcher.fetch()
    for book in books:
        print(book)
    print(f"Fetched data length: {len(books)}")


if __name__ == '__main__':

    # DI
    drive_fetcher = DriveManager(
        "https://your.google.drive.url")
    main(drive_fetcher, None)
