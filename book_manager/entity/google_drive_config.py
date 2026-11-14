from dataclasses import dataclass


@dataclass
class GoogleDriveConfig:
    """Class for storing Google drive configuration."""
    folder_id: str
