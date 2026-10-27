"""Load the indicators into the online (Neon) database.

Run from the backend folder:  python -m scripts.load_to_neon

You are asked for the Neon connection string. The input is hidden, so nothing appears when you
paste it (Ctrl+V or right-click), and it is not saved anywhere. Press Enter after pasting.
"""
import getpass
import os
import sys
from urllib.parse import urlsplit


def main() -> None:
    url = getpass.getpass("Paste the Neon connection string (hidden), then press Enter: ").strip().strip('"').strip("'")
    host = urlsplit(url).hostname or ""
    if not url.startswith(("postgresql://", "postgres://")) or not host.endswith("neon.tech"):
        sys.exit("That does not look like a Neon connection string (postgresql://...neon.tech/...). Nothing was loaded.")
    print(f"Loading into {host} ...")
    os.environ["DATABASE_URL"] = url          # must be set before the app modules read their settings
    from scripts import load_indicators

    load_indicators.main()


if __name__ == "__main__":
    main()
