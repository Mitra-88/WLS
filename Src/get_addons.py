import logging
import re
import time
import requests
from pathlib import Path
from platform import system
from urllib.parse import urlparse, parse_qs
from user_agent import get_random_user_agent
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

ID_REGEX = re.compile(r"id=(\d+)")
RATE_LIMIT = 0.5
SESSION = requests.Session()
SESSION.headers.update(
    {
        "User-Agent": get_random_user_agent(),
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
        if self.item_id:
            logger.debug(f"Created WorkshopItem: {title} (ID: {self.item_id})")
        else:
            logger.warning(f"Could not extract ID from item: {title}")

def get_collection_id(url):
    logger.debug(f"Parsing URL for collection ID: {url}")
    parsed = urlparse(url)

    if parsed.netloc not in (
        "steamcommunity.com",
        "www.steamcommunity.com",
    ):
        logger.warning(f"Invalid domain: {parsed.netloc}")
        return None

    if not parsed.path.startswith(
        ("/workshop/filedetails/", "/sharedfiles/filedetails/")
    ):
        logger.warning(f"Invalid path structure: {parsed.path}")
        return None

    ids = parse_qs(parsed.query).get("id", [])
    collection_id = ids[0] if ids and ids[0].isdigit() else None
    
    if collection_id:
        logger.info(f"Successfully extracted collection ID: {collection_id}")
    else:
        logger.error("No valid collection ID found in URL")
    
    return collection_id

def fetch_collection(url):
    logger.info(f"Fetching collection from: {url}")
    response = None

    for attempt in range(3):
        try:
            logger.debug(f"Attempt {attempt + 1}/3 - Waiting {RATE_LIMIT} seconds...")
            time.sleep(RATE_LIMIT)
            
            logger.debug("Sending HTTP request...")
            response = SESSION.get(url, timeout=30)
            
            if response.status_code == 404:
                logger.error("Collection returned 404 - Does not exist")
                raise Exception("This collection doesn't exist.")
            if response.status_code == 403:
                logger.error("Collection returned 403 - Private or unavailable")
                raise Exception("This collection is private or unavailable.")
            
            response.raise_for_status()
            logger.info(f"Successfully fetched collection (Status: {response.status_code})")
            break

        except requests.RequestException as e:
            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt == 2:
                logger.error("All 3 attempts failed to connect to Steam")
                raise Exception(
                    "Couldn't connect to Steam right now. Please try again."
                )
            logger.info("Waiting 1.5 seconds before retry...")
            time.sleep(1.5)

    logger.debug("Parsing HTML content...")
    soup = BeautifulSoup(response.text, "html.parser")
    items = []
    
    collection_items = soup.find_all("div", class_="collectionItem")
    logger.info(f"Found {len(collection_items)} collection items in HTML")

    for idx, div in enumerate(collection_items, 1):
        link_tag = div.find("a", href=True)
        title_tag = div.find(class_="workshopItemTitle")

        if link_tag and title_tag:
            title = title_tag.get_text(strip=True)
            logger.debug(f"Processing item {idx}/{len(collection_items)}: {title}")
            items.append(
                WorkshopItem(
                    link_tag["href"],
                    title,
                )
            )
        else:
            logger.warning(f"Skipping malformed item at position {idx}")

    logger.info(f"Successfully extracted {len(items)} valid items from collection")
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
            logger.info(f"User selected export mode: {options[choice][0]}")
            return options[choice]

        logger.warning(f"Invalid choice entered: {choice}")
        print("Please choose a number from 1 to 5.")

def generate_content(items, mode, tool, app_id):
    valid_items = [item for item in items if item.item_id]
    
    invalid_count = len(items) - len(valid_items)
    if invalid_count > 0:
        logger.warning(f"Skipping {invalid_count} items with missing IDs")
    
    logger.info(f"Generating {mode} output for {len(valid_items)} items (App ID: {app_id})")

    if mode == "steam":
        content = "\n".join(
            f"workshop_download_item {app_id} {item.item_id}"
            for item in valid_items
        )
        logger.debug(f"Generated {len(valid_items)} SteamCMD commands")
        return content

    if mode == "depot":
        content = "\n".join(
            f"{tool} -app {app_id} -pubfile {item.item_id}"
            for item in valid_items
        )
        logger.debug(f"Generated {len(valid_items)} DepotDownloader commands")
        return content

    if mode == "links":
        content = "\n".join(item.link for item in valid_items)
        logger.debug(f"Generated {len(valid_items)} workshop links")
        return content

    if mode == "ids":
        content = "\n".join(item.item_id for item in valid_items)
        logger.debug(f"Generated {len(valid_items)} item IDs")
        return content

    logger.warning(f"Unknown mode: {mode}")
    return ""

def write_file(path, content):
    logger.info(f"Writing to file: {path}")
    logger.debug(f"Creating parent directories: {path.parent}")
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        file.write(content)
    
    file_size = path.stat().st_size
    logger.info(f"Successfully wrote {file_size} bytes to {path}")

def confirm_overwrite(path):
    logger.debug(f"Checking if file exists: {path}")
    while True:
        reply = input(
            f"\n'{path}' already exists.\nReplace it? (y/n): "
        ).strip().lower()

        if reply in ("y", "yes"):
            logger.info(f"User confirmed overwrite of {path}")
            return True

        if reply in ("n", "no"):
            logger.info(f"User declined to overwrite {path}")
            return False

        logger.debug(f"Invalid confirmation response: {reply}")
        print("Please type y or n.")

def preview_items(items):
    print("\nCollection Preview:\n")
    logger.info(f"Previewing {len(items)} items")

    for index, item in enumerate(items, 1):
        suffix = "(missing ID)" if not item.item_id else ""
        print(f"{index}. {item.title}{suffix}")
        if not item.item_id:
            logger.debug(f"Item {index} has no ID: {item.title}")

def main():    
    url = input("\nPaste the Steam collection URL: ").strip()
    logger.info(f"User provided URL: {url}")

    logger.info("Validating collection URL...")
    collection_id = get_collection_id(url)

    if not collection_id:
        print("That doesn't look like a valid Steam collection link.")
        logger.error("Invalid URL - cannot proceed")
        return

    print("\nLoading collection...")
    logger.info("Starting collection fetch process")

    try:
        items = fetch_collection(url)
    except Exception as error:
        print(f"\n{error}")
        logger.error(f"Failed to fetch collection: {error}")
        return

    if not items:
        print("\nNo items were found in this collection.")
        logger.warning("Collection is empty or couldn't be parsed")
        return

    print(f"\nFound {len(items)} items in the collection.")
    logger.info(f"Collection contains {len(items)} total items")

    user_input = input("\n🎮 Enter App ID (Press Enter for Garry's Mod - 4000): ").strip()
    app_id = user_input if user_input else "4000"
    logger.info(f"Using App ID: {app_id}")

    mode, tool = get_choice()

    if mode == "preview":
        preview_items(items)
        logger.info("Preview mode completed")
        return

    print("\nGenerating output...")
    content = generate_content(items, mode, tool, app_id)

    if not content:
        print("Nothing to export.")
        logger.error("No valid content generated for export")
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
    logger.info(f"Output will be saved as: {output_file}")

    if output_file.exists():
        print(f"\n⚠️ File already exists: {output_file}")
        if not confirm_overwrite(output_file):
            print("❌ Operation cancelled.")
            logger.info("User cancelled due to existing file")
            return

    try:
        print("\nSaving file...")
        write_file(output_file, content + "\n")
        print(f"\nSaved successfully to: {output_file}")
        logger.info("Export completed successfully")
        print(f"\nSummary: Exported {len([i for i in items if i.item_id])} items to {output_file}")
    except OSError as e:
        print("\nCouldn't save the file. Please check permissions and try again.")
        logger.error(f"File write failed: {e}")
