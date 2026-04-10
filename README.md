# WorkshopLinkStealer

**WLS** is a command-line tool designed to fetch addon links from Steam Workshop collections and provide multiple output options for managing addons. For users who use tools like SteamCMD or DepotDownloader to download Steam Workshop content.

## Features

- 🖥️ **Cross-Platform:** Works on Windows, macOS, and Linux.
- 🌐 **Steam Collection Scraping:** Extracts addon links from Steam Workshop collection URLs.
- 📋 **Multiple Output Options:**
  - Generate SteamCMD download commands.
  - Generate DepotDownloader download commands.
  - Save full addon URLs.
  - Save only addon IDs.

## Requirements

| Operating System | Supported Versions                                       | Architecture |
|------------------|----------------------------------------------------------|--------------|
| Windows          | 11, 10                                                   | 64-bit       |
| Linux            | Debian 13, Ubuntu 24.04, Fedora 40, Arch Linux, OpenSUSE | 64-bit       |
| macOS            | macOS 26, 15, 14, 13, 12                                 | ARM64        |

- **RAM Usage:** 20MB
- **Disk Space:** 25MB

## Installation

Download the latest release from [GitHub Releases](https://github.com/VermeilChan/WLS/releases/latest):
- **Windows:** `WLS-1.x.x-Windows-x64.zip`
- **Linux:** `WLS-1.x.x-Linux-x64.zip`
- **macOS:** `WLS-1.x.x-macOS-ARM64.zip`

## Usage

When you run the program, you’ll be prompted to select from several options:

### 1. **Enter Steam Collection URL:**
Provide a Workshop collection URL to extract addon links.

### 2. **Choose an Option:**
After fetching the collection data, you can choose what to do next:
- **Generate SteamCMD Download Commands:** Creates download commands for SteamCMD.
- **Generate DepotDownloader Commands:** Creates download commands for DepotDownloader.
- **List Addon Links:** Outputs only the addon URLs.
- **List Addon IDs:** Extracts only the addon IDs.

### 3. **Save Results:**
The results (links or commands) will be saved to a text file named `addon_links-<collection_id>.txt`.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss changes.

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

## Credits

- **[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/):** For HTML parsing and web scraping.
- **[Requests](https://docs.python-requests.org/en/latest/):** For handling HTTP requests.
- **[PyInstaller](https://pyinstaller.org/en/stable/):** For creating standalone executables.
