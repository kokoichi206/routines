from dataclasses import dataclass


@dataclass
class NotionAPIConfig:
    """Class for storing Notion API configuration."""
    database_id: str
    api_key: str
