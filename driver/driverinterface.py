from .options import BrowserOptions
try:
    from abc import ABC
    from selenium import webdriver
    from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
except ImportError as err:
    print("Unable to import: {}".format(err))
    exit()


class DriverInterface(ABC):
    def factory(self) -> object:
        """Factory function returns driver object"""


class Chrome(DriverInterface):

    def __init__(self, executable_path: str,
                 chrome_options: BrowserOptions) -> None:
        self.executable_path = executable_path
        self.chrome_options = chrome_options

    def factory(self) -> object:
        return webdriver.Chrome(
            executable_path=self.executable_path, chrome_options=self.chrome_options)


class Firefox(DriverInterface):

    def __init__(self, executable_path: str, firefox_options: BrowserOptions,
                 firefox_profile: FirefoxProfile = FirefoxProfile(), binary_path: str = None) -> None:
        self.executable_path = executable_path
        self.binary_path = binary_path
        self.firefox_profile = firefox_profile
        self.firefox_options = firefox_options

    def factory(self) -> object:
        try:
            return webdriver.Firefox(executable_path=self.executable_path,
                                     firefox_options=self.firefox_options, firefox_profile=self.firefox_profile, firefox_binary=self.binary_path)
        except Exception as err:
            print(err)


class Safari(DriverInterface):

    def __init__(self, service_args: BrowserOptions, executable_path: str = "/usr/bin/safaridriver") -> None:
        self.executable_path = executable_path
        self.service_args = service_args

    def factory(self) -> object:
        try:
            return webdriver.Safari(executable_path=self.executable_path, service_args=self.service_args)
        except Exception as err:
            print(err)
