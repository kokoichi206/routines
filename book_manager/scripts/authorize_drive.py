import argparse
import os
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow


def main() -> None:
    parser = argparse.ArgumentParser(description="Authorize read-only Drive metadata access.")
    parser.add_argument("client_json", type=Path)
    parser.add_argument("output_json", type=Path)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    flow = InstalledAppFlow.from_client_secrets_file(
        str(args.client_json),
        scopes=["https://www.googleapis.com/auth/drive.metadata.readonly"],
    )
    credentials = flow.run_local_server(
        port=0,
        open_browser=not args.no_browser,
        prompt="consent",
        timeout_seconds=3600,
    )
    with os.fdopen(os.open(args.output_json, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "w") as output:
        output.write(credentials.to_json(strip=["token", "expiry"]))
    print(f"OAuth credentials saved to {args.output_json}")


if __name__ == "__main__":
    main()
