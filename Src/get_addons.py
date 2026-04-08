import os
import re
import tempfile
import time
from pathlib import Path
from platform import system
from urllib.parse import urlparse, parse_qs
import requests
from bs4 import BeautifulSoup

APP_ID = 4000
ID_REGEX = re.compile(r'id=(\d+)')
RATE_LIMIT = 0.5

class WorkshopItem:
    def __init__(self, link, title):
        self.link = link
        self.title = title
        match = ID_REGEX.search(link)
        self.item_id = match.group(1) if match else None

def get_collection_id(url):
    try:
        parsed = urlparse(url)
        if parsed.netloc not in ('steamcommunity.com', 'www.steamcommunity.com'):
            return None
        if not parsed.path.startswith(('/workshop/filedetails/', '/sharedfiles/filedetails/')):
            return None
        ids = parse_qs(parsed.query).get('id', [])
        return ids[0] if ids and ids[0].isdigit() else None
    except Exception:
        return None

def fetch_collection(url):
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://steamcommunity.com/',
        'Accept-Language': 'en-US,en;q=0.9',
    })
    session.cookies.update({'birthtime': '0', 'mature_content': '1'})
    
    last_request = 0
    resp = None
    
    for attempt in range(3):
        elapsed = time.time() - last_request
        if elapsed < RATE_LIMIT:
            time.sleep(RATE_LIMIT - elapsed)
        last_request = time.time()
        
        try:
            resp = session.get(url, timeout=30)
            resp.raise_for_status()
            break
        except requests.HTTPError:
            if resp.status_code in (403, 404):
                raise Exception(f"Collection not accessible ({resp.status_code})")
            if attempt == 2:
                raise Exception("Steam request failed after 3 retries")
            time.sleep(2 ** attempt)
        except Exception:
            if attempt == 2:
                raise Exception("Network error after 3 retries")
            time.sleep(2 ** attempt)
    
    items = []
    for div in BeautifulSoup(resp.text, 'html.parser').find_all('div', class_='collectionItem'):
        a = div.find('a', href=True)
        title = div.find(class_='workshopItemTitle')
        if a and title:
            items.append(WorkshopItem(a['href'], title.get_text(strip=True)))
    
    return items

def atomic_write(filepath, content):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    fd = None
    temp = None
    try:
        fd, temp = tempfile.mkstemp(dir=filepath.parent, suffix='.tmp')
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(content)
            fd = None
        os.replace(temp, filepath)
    finally:
        if fd:
            os.close(fd)
        if temp and os.path.exists(temp):
            os.unlink(temp)

def get_choice():
    depot = "DepotDownloader.exe" if system() == "Windows" else "DepotDownloader"
    while True:
        print("\n1. SteamCMD  2. DepotDownloader  3. Links  4. IDs  5. Preview")
        c = input("Choice (1-5): ").strip()
        if c == '1': return 'steam', None
        if c == '2': return 'depot', depot
        if c == '3': return 'links', None
        if c == '4': return 'ids', None
        if c == '5': return 'dry', None
        print("Invalid")

def generate_content(items, mode, tool):
    valid = [i for i in items if i.item_id]
    if mode == 'steam':
        return '\n'.join(f"workshop_download_item {APP_ID} {i.item_id}" for i in valid) + '\n'
    if mode == 'depot':
        return '\n'.join(f"{tool} -app {APP_ID} -pubfile {i.item_id}" for i in valid) + '\n'
    if mode == 'links':
        return '\n'.join(i.link for i in valid) + '\n'
    if mode == 'ids':
        return '\n'.join(i.item_id for i in valid) + '\n'
    return ''

def confirm(filepath):
    while True:
        r = input(f"'{filepath}' exists. Overwrite? (y/n): ").strip().lower()
        if r == 'y': return True
        if r == 'n': return False
        print("Enter y or n")

def main():
    url = input("Enter Steam collection URL: ").strip()
    cid = get_collection_id(url)
    if not cid:
        print("Error: Invalid URL")
        return
    
    try:
        items = fetch_collection(url)
    except Exception as e:
        print(f"Error: {e}")
        return
    
    if not items:
        print("No items found (empty/private collection)")
        return
    
    print(f"\nFound {len(items)} items")
    mode, tool = get_choice()
    
    if mode == 'dry':
        for i, item in enumerate(items, 1):
            print(f"{i}. {item.title} {'(no ID)' if not item.item_id else ''}")
        return
    
    content = generate_content(items, mode, tool)
    if not content:
        return
    
    suffix = {'steam': 'steamcmd', 'depot': 'depotdownloader'}.get(mode, mode)
    path = Path(f'addon_{suffix}-{cid}.txt')
    
    if path.exists() and not confirm(path):
        print("Cancelled")
        return
    
    try:
        atomic_write(path, content)
        print(f"Saved to {path}")
    except Exception as e:
        print(f"Write error: {e}")
