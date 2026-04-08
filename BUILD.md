# Table of Contents

- [Platforms](#platforms)
- [Getting the Source Code](#getting-the-source-code)
- [Dependencies](#dependencies)
  - [Windows/macOS](#dependencies)
  - [Linux](#linux-dependencies)
- [Compiling](#compiling)
  - [Windows](#windows-details)
  - [Linux/macOS](#linux-details)

# Platforms

WorkshopLinkStealer supports the following platforms:

| Operating System | Supported Versions                                       | Architecture |
|------------------|----------------------------------------------------------|--------------|
| Windows          | 11, 10,                                                  | 64-bit       |
| Linux            | Debian 13, Ubuntu 24.04, Fedora 43, Arch Linux, OpenSUSE | 64-bit       |
| macOS            | macOS 26, 14, 13, 12                                     | ARM64        |

# Getting the Source Code

- Download the zip archive from the [latest release](https://github.com/Mitra-88/WorkshopLinkStealer/releases/latest). `Source code (zip)`

# Dependencies

You need the following to compile WorkshopLinkStealer:

- [Python](https://www.python.org/) 3.12+
- [PyInstaller](https://www.pyinstaller.org/) 6.19.0+
- [Beautiful Soup](https://pypi.org/project/beautifulsoup4/) 4.14.3+
- [Requests](https://pypi.org/project/requests/) 2.33.1+

## Linux Dependencies

For Ubuntu/Debian:
```sh
sudo apt install -y python3 python3-pip python3-venv
```
For Fedora:
```sh
sudo dnf install -y python3 python3-pip python3-virtualenv
```
For Arch:
```sh
sudo pacman -Syu --noconfirm python-pip python-virtualenv
```
For OpenSUSE:
```sh
sudo zypper install -y python3 python3-pip python3-virtualenv
```

# Compiling

## Windows

In Command Prompt:
```sh
cd WLS
py -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
pyinstaller --noconfirm --onefile --console --icon "Src/Icon/WorkshopLinkStealer.ico" --name "WLS" --clean --optimize "2" --version-file "version.txt" --add-data "Src/get_addons.py;." --add-data "Src/utils.py;."  "Src/cli.py"
```

## Linux/macOS

In Terminal:
```sh
cd WLS
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pyinstaller --noconfirm --onefile --console --name "WLS" --clean --optimize "2" --strip --add-data "Src/get_addons.py:." --add-data "Src/utils.py:."  "Src/cli.py"
```
