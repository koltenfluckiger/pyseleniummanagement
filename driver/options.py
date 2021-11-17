try:
    from abc import ABC
    from typing import List
except ImportError as err:
    print("Unable to import: {}".format(err))
    exit()

from selenium.webdriver.firefox.options import Options as FirefoxOpts
from selenium.webdriver.chrome.options import Options as ChromeOpts
from selenium.webdriver.safari.service import Service as SafariOpts

class BrowserOptions(ABC):

    def factory(self) -> object:
        """Factory function returning options object"""


class ChromeOptions(BrowserOptions):

    def __init__(self, arguments: List[str] = [],
                 extension_paths: List[str] = [], binary_path:str=None) -> None:
        self.arguments = arguments
        self.extension_paths = extension_paths
        self.binary_path = binary_path

    def factory(self) -> object:
        try:
            options = ChromeOpts()
            for arg in self.arguments:
                options.add_argument(arg)
            for ext_path in self.extension_paths:
                options.add_extension(ext_path)
            if self.binary_path:
                options.binary_location = self.binary_path
            self.options = options
            return options
        except Exception as err:
            print(err)


class FirefoxOptions(BrowserOptions):

    def __init__(self, arguments: List[str] = [],
                 extension_paths: List[str] = []) -> None:
        self.arguments = arguments
        self.extension_paths = extension_paths

    def factory(self) -> object:
        try:
            options = FirefoxOpts()
            for arg in self.arguments:
                options.add_argument(arg)
            for ext_path in self.extension_paths:
                options.add_extension(ext_path)
            self.options = options
            return options
        except Exception as err:
            print(err)


class SafariOptions(BrowserOptions):

    def __init__(self, executable_path:str, arguments: List[str] = []) -> None:
        self.executable_path = executable_path
        self.arguments = arguments

    def factory(self) -> List:
        try:
            opts = []
            for arg in self.arguments:
                opts.append(arg)
            self.opts = opts
            service = Service(executable_path=self.executable_path, service_args=opts)
            return service
        except Exception as err:
            print(err)
