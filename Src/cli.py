import sys
from get_addons import main as get_addons_links
from utils import get_system_info, wly_version, build_date, requests_version, beautifulsoup4_version, pyinstaller_version

def display_info():
    print(
        f"WorkshopLinkStealer {wly_version}, {get_system_info()}.\n"
        f"Build Date: {build_date}.\n"
        f"Build Info: Pyinstaller {pyinstaller_version}, BeautifulSoup4 {beautifulsoup4_version}, "
        f"Requests {requests_version}.\n"
    )

def display_menu():
    print(
        "Select an option:\n"
        "1. Get addons links\n"
        "2. Exit\n"
    )

def handle_choice(choice):
    options = {
        "1": get_addons_links,
        "2": sys.exit
    }

    if choice in options:
        options[choice]()
    else:
        print("Please enter a number from 1 to 2.")

def main():
    try:
        display_info()
        while True:
            display_menu()
            handle_choice(input("Enter your choice (1-2): ").strip())
    except (KeyboardInterrupt, EOFError):
        print("\nExiting...")
        sys.exit(0)

if __name__ == "__main__":
    main()
