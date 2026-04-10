import re
import time
import requests
from pathlib import Path
from platform import system
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup

ID_REGEX = re.compile(r"id=(\d+)")
RATE_LIMIT = 0.5
SESSION = requests.Session()
SESSION.headers.update(
    {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/146.0.0.0 Safari/537.36"
        ),
        "Referer": "https://steamcommunity.com/",
        "Accept-Language": "en-US,en;q=0.9",
    }
)
SESSION.cookies.update(
    {
        "birthtime": "0",
        "mature_content": "1",
    }
)

class WorkshopItem:
    def __init__(self, link, title):
        self.link = link
        self.title = title
        match = ID_REGEX.search(link)
        self.item_id = match.group(1) if match else None

def get_collection_id(url):
    parsed = urlparse(url)

    if parsed.netloc not in (
        "steamcommunity.com",
        "www.steamcommunity.com",
    ):
        return None

    if not parsed.path.startswith(
        ("/workshop/filedetails/", "/sharedfiles/filedetails/")
    ):
        return None

    ids = parse_qs(parsed.query).get("id", [])
    return ids[0] if ids and ids[0].isdigit() else None

def fetch_collection(url):
    response = None

    for attempt in range(3):
        try:
            time.sleep(RATE_LIMIT)
            response = SESSION.get(url, timeout=30)
            if response.status_code == 404:
                raise Exception("This collection doesn't exist.")
            if response.status_code == 403:
                raise Exception("This collection is private or unavailable.")
            response.raise_for_status()
            break

        except requests.RequestException:
            if attempt == 2:
                raise Exception(
                    "Couldn't connect to Steam right now. Please try again."
                )
            time.sleep(1.5)

    soup = BeautifulSoup(response.text, "html.parser")
    items = []

    for div in soup.find_all("div", class_="collectionItem"):
        link_tag = div.find("a", href=True)
        title_tag = div.find(class_="workshopItemTitle")

        if link_tag and title_tag:
            items.append(
                WorkshopItem(
                    link_tag["href"],
                    title_tag.get_text(strip=True),
                )
            )

    return items

def get_choice():
    depot = (
        "DepotDownloader.exe"
        if system() == "Windows"
        else "DepotDownloader"
    )

    options = {
        "1": ("steam", None),
        "2": ("depot", depot),
        "3": ("links", None),
        "4": ("ids", None),
        "5": ("preview", None),
    }

    while True:
        print("\nWhat would you like to export?")
        print("  1) SteamCMD commands")
        print("  2) DepotDownloader commands")
        print("  3) Workshop links")
        print("  4) Item IDs only")
        print("  5) Preview items only")

        choice = input("\nChoose (1-5): ").strip()

        if choice in options:
            return options[choice]

        print("Please choose a number from 1 to 5.")

def generate_content(items, mode, tool, app_id):
    valid_items = [item for item in items if item.item_id]

    if mode == "steam":
        return "\n".join(
            f"workshop_download_item {app_id} {item.item_id}"
            for item in valid_items
        )

    if mode == "depot":
        return "\n".join(
            f"{tool} -app {app_id} -pubfile {item.item_id}"
            for item in valid_items
        )

    if mode == "links":
        return "\n".join(item.link for item in valid_items)

    if mode == "ids":
        return "\n".join(item.item_id for item in valid_items)

    return ""

def write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        file.write(content)

def confirm_overwrite(path):
    while True:
        reply = input(
            f"\n'{path}' already exists.\nReplace it? (y/n): "
        ).strip().lower()

        if reply in ("y", "yes"):
            return True

        if reply in ("n", "no"):
            return False

        print("Please type y or n.")

def preview_items(items):
    print("\nCollection Preview:\n")

    for index, item in enumerate(items, 1):
        suffix = " (missing ID)" if not item.item_id else ""
        print(f"{index}. {item.title}{suffix}")

def main():
    url = input("\nPaste the Steam collection URL: ").strip()

    collection_id = get_collection_id(url)

    if not collection_id:
        print("That doesn't look like a valid Steam collection link.")
        return

    print("\nLoading collection...")

    try:
        items = fetch_collection(url)
    except Exception as error:
        print(f"\n{error}")
        return

    if not items:
        print("\nNo items were found in this collection.")
        return

    print(f"\nFound {len(items)} items.")

    user_input = input("\nEnter App ID (Press Enter for Garry's Mod - 4000): ").strip()
    app_id = user_input if user_input else "4000"

    mode, tool = get_choice()

    if mode == "preview":
        preview_items(items)
        return

    content = generate_content(items, mode, tool, app_id)

    if not content:
        print("Nothing to export.")
        return

    suffix_map = {
        "steam": "steamcmd",
        "depot": "depotdownloader",
        "links": "links",
        "ids": "ids",
    }

    output_file = Path(
        f"addon_{suffix_map[mode]}-{collection_id}.txt"
    )

    if output_file.exists():
        if not confirm_overwrite(output_file):
            print("Cancelled.")
            return

    try:
        write_file(output_file, content + "\n")
        print(f"\nSaved successfully to: {output_file}")
    except OSError:
        print("\nCouldn't save the file. Please try again.")
