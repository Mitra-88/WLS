import random
from dataclasses import dataclass

@dataclass
class BrowserProfile:
    browser: str
    platform: str
    mobile: bool

class UserAgentGenerator:
    def __init__(self):
        self.browser_weights = {
            "chrome": 50,
            "edge": 15,
            "firefox": 10,
            "safari": 15,
            "opera": 5,
            "brave": 3,
            "vivaldi": 2,
        }

        self.platform_weights = {
            "windows": 35,
            "macos": 15,
            "linux": 8,
            "android": 27,
            "iphone": 10,
            "ipad": 5,
        }

        self.windows_versions = [
            "Windows NT 10.0; Win64; x64",
            "Windows NT 10.0; WOW64",
            "Windows NT 10.0; Win64; ARM64",
            "Windows NT 11.0; Win64; x64",
            "Windows NT 11.0; Win64; ARM64",
            "Windows NT 6.3; Win64; x64",
        ]

        self.macos_versions = [
            "Macintosh; Intel Mac OS X 10_13_6",
            "Macintosh; Intel Mac OS X 10_14_6",
            "Macintosh; Intel Mac OS X 10_15_7",
            "Macintosh; Intel Mac OS X 11_7_10",
            "Macintosh; Intel Mac OS X 12_7_4",
            "Macintosh; Intel Mac OS X 13_6_6",
            "Macintosh; Intel Mac OS X 14_5_0",
            "Macintosh; Intel Mac OS X 15_0_0",
            "Macintosh; Apple Silicon Mac OS X 14_5_0",
            "Macintosh; Apple Silicon Mac OS X 15_0_0",
        ]

        self.linux_versions = [
            "X11; Linux x86_64",
            "X11; Ubuntu; Linux x86_64",
            "X11; Fedora; Linux x86_64",
            "X11; Debian; Linux x86_64",
            "X11; Arch Linux; Linux x86_64",
        ]

        self.android_devices = [
            "Android 10; SM-G973F",
            "Android 11; SM-G991B",
            "Android 12; SM-G998B",
            "Android 13; SM-S911B",
            "Android 14; SM-S918B",
            "Android 14; SM-S926B",
            "Android 15; SM-S928B",

            "Android 11; Pixel 5",
            "Android 12; Pixel 6",
            "Android 13; Pixel 7",
            "Android 14; Pixel 8",
            "Android 14; Pixel 8 Pro",
            "Android 15; Pixel 9 Pro",

            "Android 10; Redmi Note 9",
            "Android 11; Redmi Note 10 Pro",
            "Android 12; Redmi Note 11",
            "Android 13; Redmi Note 12",
            "Android 14; Redmi Note 13 Pro",

            "Android 13; OnePlus 11",
            "Android 14; OnePlus 12",
            "Android 15; OnePlus 13",

            "Android 12; M2101K9G",
            "Android 13; 22101320G",
        ]

        self.ipad_devices = [
            "iPad; CPU OS 15_7 like Mac OS X",
            "iPad; CPU OS 16_7 like Mac OS X",
            "iPad; CPU OS 17_0 like Mac OS X",
            "iPad; CPU OS 18_0 like Mac OS X",
        ]

        self.ios_devices = [
            "iPhone; CPU iPhone OS 14_8 like Mac OS X",
            "iPhone; CPU iPhone OS 15_7 like Mac OS X",
            "iPhone; CPU iPhone OS 16_7 like Mac OS X",
            "iPhone; CPU iPhone OS 17_0 like Mac OS X",
            "iPhone; CPU iPhone OS 17_6 like Mac OS X",
            "iPhone; CPU iPhone OS 18_0 like Mac OS X",
            "iPhone; CPU iPhone OS 18_4 like Mac OS X",
        ]
    def weighted_choice(self, choices: dict):
        items = list(choices.keys())
        weights = list(choices.values())
        return random.choices(items, weights=weights, k=1)[0]

    def chrome_version(self):
        major = random.choice([122, 123, 124, 125, 126, 127, 128, 129, 130, 131])
        build = random.randint(6000, 6999)
        patch = random.randint(50, 200)
        return f"{major}.0.{build}.{patch}"

    def firefox_version(self):
        major = random.choice([123, 124, 125, 126, 127, 128])
        return f"{major}.0"

    def safari_webkit(self):
        return f"605.1.{random.randint(10, 30)}"

    def get_platform_string(self, platform):
        if platform == "windows":
            return random.choice(self.windows_versions)
        if platform == "macos":
            return random.choice(self.macos_versions)
        if platform == "linux":
            return "X11; Linux x86_64"
        if platform == "android":
            return random.choice(self.android_devices)
        if platform == "iphone":
            return random.choice(self.ios_devices)

    def compatible_browser(self, platform):
        if platform == "iphone":
            return "safari"

        if platform == "macos":
            return random.choices(
                ["chrome", "firefox", "safari", "edge"],
                weights=[40, 15, 35, 10],
                k=1
            )[0]

        if platform == "android":
            return random.choices(
                ["chrome", "firefox", "opera"],
                weights=[75, 10, 15],
                k=1
            )[0]

        return self.weighted_choice(self.browser_weights)

    def generate(self):
        platform = self.weighted_choice(self.platform_weights)
        browser = self.compatible_browser(platform)
        platform_string = self.get_platform_string(platform)

        if browser == "chrome":
            version = self.chrome_version()
            return (
                f"Mozilla/5.0 ({platform_string}) "
                f"AppleWebKit/537.36 (KHTML, like Gecko) "
                f"Chrome/{version} Safari/537.36"
            )

        elif browser == "edge":
            chrome_ver = self.chrome_version()
            edge_ver = chrome_ver
            return (
                f"Mozilla/5.0 ({platform_string}) "
                f"AppleWebKit/537.36 (KHTML, like Gecko) "
                f"Chrome/{chrome_ver} Safari/537.36 "
                f"Edg/{edge_ver}"
            )

        elif browser == "firefox":
            version = self.firefox_version()
            return (
                f"Mozilla/5.0 ({platform_string}; rv:{version}) "
                f"Gecko/20100101 Firefox/{version}"
            )

        elif browser == "safari":
            webkit = self.safari_webkit()
            safari_version = random.choice(["16.6", "17.0", "17.2", "17.4"])
            return (
                f"Mozilla/5.0 ({platform_string}) "
                f"AppleWebKit/{webkit} (KHTML, like Gecko) "
                f"Version/{safari_version} Safari/{webkit}"
            )

        elif browser == "opera":
            chrome_ver = self.chrome_version()
            opera_major = random.randint(105, 115)
            return (
                f"Mozilla/5.0 ({platform_string}) "
                f"AppleWebKit/537.36 (KHTML, like Gecko) "
                f"Chrome/{chrome_ver} Safari/537.36 "
                f"OPR/{opera_major}.0.{random.randint(4000, 9999)}.{random.randint(10, 150)}"
            )

def get_random_user_agent():
    return UserAgentGenerator().generate()
