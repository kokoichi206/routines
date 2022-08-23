import os

import config.google_drive_config as google_drive_config
import config.notion_config as notion_config
from entity.google_drive_config import GoogleDriveConfig
from entity.notion_config import NotionAPIConfig


def load_notion_config() -> NotionAPIConfig:
    """Load configuration about Notion API.

    The order of priority:
    1. Environment variable
    2. notion_config.py file

    Returns:
        API configuration (:class:`NotionAPIConfig`): Entity about API configuration.
    """

    database_id = os.getenv("DATABASE_ID")
    if not database_id:
        database_id = notion_config.DATABASE_ID

    secret = os.getenv("NOTION_API_SECRET")
    if not secret:
        secret = notion_config.NOTION_API_SECRET

    return NotionAPIConfig(
        database_id=database_id,
        api_key=secret,
    )


def load_google_drive_config() -> GoogleDriveConfig:
    """Load configuration about Google Drive.

    The order of priority:
    1. Environment variable
    2. google_drive_config.py file

    Returns:
        Google Drive configuration (:class:`GoogleDriveConfig`): Entity about Google Drive configuration.
    """

    drive_url = os.getenv("GOOGLE_DRIVE_URL")
    if not drive_url:
        drive_url = google_drive_config.GOOGLE_DRIVE_URL

    return GoogleDriveConfig(
        url=drive_url,
    )
