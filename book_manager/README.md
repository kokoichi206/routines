# Book Manager

## Google Drive

### Feature

- Fetch

### Setup

1. Prepare your Google Drive URL
   - Environment variable or `google_drive_config.py` file

```sh
# Setup your Google Drive URL
# as environment variables or in google_drive_config.py file

# Environment
$ echo ${GOOGLE_DRIVE_URL}
https://foo.bar.foobar/path/to/google.drive

# google_drive_config.py
$ cat config/google_drive_config.py
GOOGLE_DRIVE_URL = "https://foo.bar.foobar/path/to/google.drive"
```

## Notion

### Feature

- Fetch
- Upload

### Setup

1. Prepare your Notion API key and database_id
   - Environment variable or `notion_config.py` file

```sh
# Setup your Notion API key and database_id
# as environment variables or in notion_config.py file

# Environment
$ echo ${DATABASE_ID}
https://foo.bar.foobar/path/to/google.drive
$ echo ${NOTION_API_SECRET}
https://foo.bar.foobar/path/to/google.drive

# notion_config.py
$ cat config/notion_config.py
DATABASE_ID = "7nclcd2a1da94ae5tgf0349e1co0ief2"
NOTION_API_SECRET = "secret_PoqeS4gMy07OmbMNIkfUDbaA4rt5TUfa8npemQo00mx"
```
