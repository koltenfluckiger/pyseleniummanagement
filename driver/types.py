try:
    from enum import Enum
    from selenium.webdriver.common.keys import Keys
except ImportError as err:
    print("Unable to import: {}".format(err))
    exit()

class MODIFERKEYS(Enum):

    CTRL = Keys.CONTROL
    ALT = Keys.ALT
    SHIFT = Keys.SHIFT
    ENTER = Keys.ENTER

    def __str__(self):
        return self.value

class DROPDOWNTYPE(Enum):

    INDEX = 1
    VALUE = 2
    TEXT = 3
