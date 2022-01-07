from .driverinterface import DriverInterface
from .wait import *
from .types import MODIFERKEYS, DROPDOWNTYPE
try:
    from enum import Enum
    from typing import Any, List
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.remote.webelement import WebElement
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support.ui import Select
    from time import sleep
    import signal
    import os
    import shutil
    import psutil
    from psutil import Process
    import re
    from pathlib import PurePath
    import logging
except ImportError as err:
    print("Unable to import: {}".format(err))
    exit()

logging.basicConfig(filename="pylibseleniummanagement.log")


class Error(Exception):
    def __init__(self, text):
        self.text = text


class DriverClient(object):

    def __init__(self, driver: DriverInterface, poll_time: int = 10, poll_frequency: int = 1, scroll_pause_time: int = 5, debug_mode: bool = False, throw: bool = False, delete_profile: bool = False, close_previous_sessions: bool = False) -> None:
        self.close_previous_sessions = close_previous_sessions
        self.debug_mode = debug_mode
        self.delete_profile = delete_profile
        self.driver = driver
        self.poll_frequency = poll_frequency
        self.poll_time = poll_time
        self.scroll_pause_time = scroll_pause_time
        self.throw = throw

    def __del__(self) -> None:
        try:
            if self.debug_mode == False:
                self._kill_processes()
                self.driver = None
            elif (self.debug_mode == False) and (self.delete_profile == True):
                self._kill_processes()
                self._delete_profile()
                self.driver = None
        except Exception as err:
            pass

    def _kill_processes(self):
        try:
            if self.driver.service.process.pid:
                pid = self.driver.service.process.pid
                p = psutil.Process(pid)
                children = p.children(recursive=True)
                children.append(p)
                for process in children:
                    try:
                        process.kill()
                    except Exception as err:
                        pass
        except Exception as err:
            pass

    def _delete_profile(self):
        try:
            browser_name = self.driver.capabilities['browserName']
            if browser_name == 'chrome':
                data_dir = self.driver.capabilities['chrome']['userDataDir']
            elif browser_name == 'firefox':
                data_dir = self.driver.capabilities['moz:profile']
            shutil.rmtree(Path(data_dir).resolve())
        except Exception as err:
            pass

    def check_throw(self, error: Error) -> None:
        if self.throw:
            raise error
        else:
            print(error)
            logging.critical(error)

    def close(self) -> None:
        try:
            self.driver.close()
        except Exception as err:
            self.check_throw(
                Error("ERROR: {}".format(err)))

    def quit(self) -> None:
        try:
            self.driver.quit()
        except Exception as err:
            self.check_throw(
                Error("ERROR: {}".format(err)))

    def go(self, url: str) -> None:
        try:
            self.driver.get(url)
        except Exception as err:
            self.check_throw(
                Error("ERROR: {}".format(err)))

    def reload(self) -> None:
        try:
            self.driver.refresh()
        except Exception as err:
            self.check_throw(
                Error("ERROR: {}".format(err)))

    def scroll_to_top(self) -> None:
        try:
            self.execute_script("window.scrollTo(0, 0);")
        except Exception as err:
            self.check_throw(
                Error("ERROR: {}".format(err)))

    def scroll_to_bottom(self, times: int) -> None:
        try:
            browser_height = self.driver.execute_script(
                "return document.body.scrollHeight")
            for i in range(0, times):
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")
                sleep(self.scroll_pause_time)
                new_browser_height = self.driver.execute_script(
                    "return document.body.scrollHeight")
                if new_browser_height == browser_height:
                    break
                browser_height = new_browser_height
        except Exception as err:
            self.check_throw(
                Error("ERROR: {}".format(err)))

    def open_new_tab(self) -> None:
        try:
            self.execute_script("window.open();")
        except Exception as err:
            self.check_throw(
                Error("ERROR: {}".format(err)))

    def open_new_tab_go(self, url: str) -> None:
        try:
            self.execute_script(
                "var newWindow = window.open(); newWindow.location.href = '{}'".format(url))
        except Exception as err:
            print(err)

    def press_modifer_key_send_keys(self, modifer_key: MODIFERKEYS, keys: Any) -> None:
        try:
            action = ActionChains(self.driver)
            action.key_down(modifer_key).send_keys(keys).key_up(modifer_key)
            action.perform()
        except Exception as err:
            self.check_throw(
                Error("ERROR: {}".format(err)))

    def press_modifer_key(self, modifer_key: MODIFERKEYS) -> None:
        try:
            action = ActionChains(self.driver)
            action.key_down(modifer_key).key_up(modifer_key)
            action.perform()
        except Exception as err:
            self.check_throw(
                Error("ERROR: {}".format(err)))

    def get_current_iframe(self):
        try:
            current_frame = self.execute_script("self.name")
            return current_frame
        except Exception as err:
            self.check_throw(Error("ERROR: {}".format(err)))

    def switch_to_iframe(self, iframe: WebElement) -> None:
        try:
            self.driver.switch_to.frame(iframe)
        except Exception as err:
            self.check_throw(
                Error("ERROR: {}".format(err)))

    def switch_to_default_iframe(self) -> None:
        try:
            self.driver.switch_to.default_content()
        except Exception as err:
            self.check_throw(
                Error("ERROR: {}".format(err)))

    def get_elements(self, xpath: str) -> WebElement:
        try:
            elements = WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.presence_of_all_elements_located((By.XPATH, xpath)))
            return elements
        except Exception as err:
            self.check_throw(
                Error("Failed to find elements: {}".format(xpath)))

    def get_element(self, xpath: str) -> WebElement:
        try:
            element = WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            return element
        except Exception as err:
            self.check_throw(Error("Failed to find element: {}".format(xpath)))

    def find_and_send_modifer_key(self, xpath: str, key: Any) -> None:
        try:
            WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            element = WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
            element.send_keys(key)
        except Exception as err:
            self.check_throw(
                Error("Failed to find element: {} and send keys: {}".format(xpath, keys)))

    def find_and_click_send_modifer_key(self, xpath: str, key: Any) -> None:
        try:
            WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            element = WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
            element.click()
            element.send_keys(key)
        except Exception as err:
            self.check_throw(
                Error("Failed to find element: {} and send keys: {}".format(xpath, keys)))

    def find_and_send_keys(self, xpath: str, keys: Any) -> None:
        try:
            WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
            WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                wait_for_keys_verification((By.XPATH, xpath), keys))
        except Exception as err:
            self.check_throw(
                Error("Failed to find element: {} and send keys: {}".format(xpath, keys)))

    def find_click_and_send_keys(self, xpath: str, keys: str) -> None:
        try:
            WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            element = WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
            element.click()
            WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                wait_for_keys_verification((By.XPATH, xpath), keys))
        except Exception as err:
            self.check_throw(Error(
                "Failed to find element: {} and send keys: {}".format(xpath, keys)))

    def find_and_click(self, xpath: str) -> None:
        try:
            WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            element = WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
            action = ActionChains(self.driver)
            action.move_to_element(element)
            action.click(element)
            action.perform()

        except Exception as err:
            self.check_throw(
                Error("Failed to find element: {} and click.".format(xpath)))

    def find_click_and_send_keys_and_go(self, xpath: str, keys: str, url: str) -> None:
        try:
            WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            element = WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
            action = ActionChains(self.driver)
            action.move_to_element(element)
            action.click(element)
            action.send_keys(keys)
            action.perform()
            self.driver.go(url)

        except Exception as err:
            self.check_throw(
                Error("Failed to find element: {} and click.".format(xpath)))

    def click_element(self, element: WebElement) -> None:
        try:
            action = ActionChains(self.driver)
            action.move_to_element(element)
            action.click(element)
            action.perform()

        except Exception as err:
            self.check_throw(Error(
                "Failed to find element: {} and click.".format(element)))

    def click_chain_elements_infinitely(self, xpaths: list, pause_time: int = 0) -> None:
        while True:
            try:
                for xpath in xpaths:
                    WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                        EC.presence_of_element_located((By.XPATH, xpath)))
                    element = WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                        EC.element_to_be_clickable((By.XPATH, xpath)))
                    action = ActionChains(self.driver)
                    action.move_to_element(element)
                    action.click(element)
                    action.perform()
                sleep(pause_time)
            except Exception as err:
                self.check_throw(
                    Error("Failed to find element: {} and click.".format(xpath)))

    def click_chain_elements(self, xpaths: list, pause_time: int = 0, loop_count: int = 10) -> None:
        try:
            for i in range(0, loop_count):
                for xpath in xpaths:
                    WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                        EC.presence_of_element_located((By.XPATH, xpath)))
                    element = WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                        EC.element_to_be_clickable((By.XPATH, xpath)))
                    action = ActionChains(self.driver)
                    action.move_to_element(element)
                    action.click(element)
                    action.perform()
                sleep(pause_time)
        except Exception as err:
            self.check_throw(
                Error("Failed to find element: {} and click.".format(xpath)))

    def click_all_elements_and_scroll(self, xpath: str, scroll_count=1) -> None:
        try:
            elements = WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.presence_of_all_elements_located((By.XPATH, xpath)))
            for element in elements:
                WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                    EC.element_to_be_clickable(element))
                action = ActionChains(self.driver)
                action.move_to_element(element)
                action.click(element)
                action.perform()

            self.scroll_to_bottom(scroll_count)
        except Exception as err:
            self.check_throw(
                Error("Failed to find element: {} and click.".format(xpath)))

    def click_and_wait_for_load(self, xpath: str):
        try:
            WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
            WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                wait_for_load_after_click((By.XPATH, xpath)))
        except Exception as err:
            print(err)
            self.check_throw(
                Error("Failed to find element: {} and click.".format(xpath)))

    def click_and_wait_for_html_load(self, xpath: str):
        try:
            WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
            WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                wait_for_html_load_after_click((By.XPATH, xpath)))
        except Exception as err:
            print(err)
            self.check_throw(
                Error("Failed to find element: {} and click.".format(xpath)))

    def click_element_and_wait_for_load(self, element: WebElement):
        try:
            WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.element_to_be_clickable(element))
            WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                wait_for_html_load_after_click_element(element))
        except Exception as err:
            print(err)
            self.check_throw(
                Error("Failed to find element: {} and click.".format(xpath)))

    def wait_for_element(self, xpath: str) -> None:
        try:
            WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
        except Exception as err:
            self.check_throw(
                Error("Failed to find element: {} and click.".format(xpath)))

    def wait_to_click_element(self, xpath: str, wait: int = 1) -> None:
        try:
            WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                wait_element_to_be_clickable((By.XPATH, xpath), wait))
        except Exception as err:
            self.check_throw(
                Error("Failed to find element: {} and click.".format(xpath)))

    def element_exists(self, xpath: str) -> bool:
        try:
            element = WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            if element:
                return True
            else:
                return False
        except Exception as err:
            return False

    def click_all_elements(self, xpath: str) -> None:
        try:
            elements = WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.presence_of_all_elements_located((By.XPATH, xpath)))
            for element in elements:
                WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                    EC.element_to_be_clickable(element))
                action = ActionChains(self.driver)
                action.move_to_element(element)
                action.click(element)
                action.perform()
        except Exception as err:
            self.check_throw(
                Error("Failed to find element: {} and click.".format(xpath)))

    def click_all_elements_and_reload(self, xpath: str) -> None:
        try:
            elements = WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.presence_of_all_elements_located((By.XPATH, xpath)))
            for element in elements:
                WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                    EC.element_to_be_clickable(element))
                action = ActionChains(self.driver)
                action.move_to_element(element)
                action.click(element)
                action.perform()

            self.driver.refresh()
        except Exception as err:
            self.check_throw(
                Error("Failed to find element: {} and click.".format(xpath)))

    def find_frame_switch(self, xpath: str) -> None:
        try:
            WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.frame_to_be_available_and_switch_to_it((By.XPATH, xpath)))
        except Exception as err:
            self.check_throw(
                Error("Failed to find element: {} and switch.".format(xpath)))

    def get_window_handles(self):
        try:
            return self.driver.window_handles
        except Exception as err:
            self.check_throw(
                Error("Failed to get current window handles. ERROR: {}".format(err)))

    def get_current_window_handle(self):
        try:
            return self.driver.current_window_handle
        except Exception as err:
            self.check_throw(
                Error("Failed to save current window handle. ERROR: {}".format(err)))

    def find_window_handle_switch_to_it_close_previous(self, index):
        try:
            WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                window_handle_to_be_available_switch_close_previous(index))
        except Exception as err:
            self.check_throw(
                Error("Failed to find window index: {} and switch.".format(index)))

    def find_window_handle_switch_to_it(self, index):
        try:
            window = WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                window_handle_to_be_available(index))
            self.driver.switch_to.window(window)
        except Exception as err:
            self.check_throw(
                Error("Failed to find window index: {} and switch.".format(index)))

    def get_window_handle_id(self, index: int) -> str:
        try:
            return self.driver.window_handles[index]
        except Exception as err:
            self.check_throw(Error("ERROR: {}".format(err)))

    def switch_to_latest_window(self) -> None:
        try:
            window = WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                window_handle_to_be_available(len(self.driver.window_handles) - 1))
            self.driver.switch_to.window(window)
        except Exception as err:
            self.check_throw(Error("ERROR: {}".format(err)))

    def switch_to_first_window(self) -> None:
        try:
            first_window_index = self.driver.window_handles[0]
            self.driver.switch_to.window(first_window_index)
        except Exception as err:
            self.check_throw(Error("ERROR: {}".format(err)))

    def close_current_window(self) -> None:
        try:
            self.driver.close()
        except Exception as err:
            self.check_throw(Error("ERROR: {}".format(err)))

    def switch_to_parent_frame(self) -> None:
        try:
            self.driver.switch_to.parent_frame()
        except Exception as err:
            self.check_throw(Error("ERROR: {}".format(err)))

    def check_element_for_value_change(self, xpath: str, forever=False):
        if forever:
            value_changed = not False
            while value_changed:
                try:
                    WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                        wait_for_value_to_change((By.XPATH, xpath)))
                    value_changed = not True
                except Exception as err:
                    self.check_throw(Error("ERROR: {}".format(err)))
        else:
            try:
                WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                    wait_for_value_to_change((By.XPATH, xpath)))
            except Exception as err:
                self.check_throw(Error("ERROR: {}".format(err)))

    def check_node_css_property(self, xpath: str, property: str, search: str, value: str, return_value=False) -> Any:
        try:
            search_str = re.compile(search)
            element = WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            element_property = element.value_of_css_property(property)
            match = search_str.findall(element_property)
            if match:
                match_str = match.group(1)
                if match_str == value:
                    if return_value:
                        return match_str
                    else:
                        return True
                else:
                    if return_value:
                        return element_property
                    return False
            else:
                return False

        except Exception as err:
            self.check_throw(Error("ERROR: {}".format(err)))

    def execute_script(self, script: str, return_value=False, node: WebElement = None) -> Any:
        try:
            if return_value:
                value = self.driver.execute_script(script)
                return value
            else:
                self.driver.execute_script(script)
        except Exception as err:
            self.check_throw(Error("ERROR: {}".format(err)))

    def execute_async_script(self, script: str, return_value=False) -> Any:
        try:
            if return_value:
                value = self.driver.execute_async_script(script)
                return value
            else:
                self.driver.execute_async_script(script)
        except Exception as err:
            self.check_throw(Error("ERROR: {}".format(err)))

    def get_text_from_node_convert(self, xpath: str, ctype: Any) -> Any:
        try:
            element = WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
            return ctype(element.text)
        except Exception as err:
            self.check_throw(Error("ERROR: {}".format(err)))

    def get_text_from_node(self, xpath: str) -> str:
        try:
            element = WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
            return element.text
        except Exception as err:
            self.check_throw(Error("ERROR: {}".format(err)))

    def set_attribute_of_node(self, xpath: str, attribute: str, value: str) -> None:
        try:
            element = WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            self.execute_script("document.evaluate('{}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.setAttribute('{}', '{}')".format(
                xpath, attribute, value))
        except Exception as err:
            self.check_throw(Error("ERROR: {}".format(err)))

    def remove_attribute_of_node(self, xpath: str, attribute: str) -> None:
        try:
            element = WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            self.execute_script(
                "document.evaluate('{}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.removeAttribute('{}');".format(xpath, attribute))
        except Exception as err:
            self.check_throw(Error("ERROR: {}".format(err)))

    def get_property_from_node(self, xpath: str, attr: str) -> Any:
        try:
            element = WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
            return element.get_property(attr)
        except Exception as err:
            self.check_throw(Error("ERROR: {}".format(err)))

    def get_attribute_from_node(self, xpath: str, attr: str) -> Any:
        try:
            element = WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            return element.get_attribute(attr)
        except Exception as err:
            self.check_throw(Error("ERROR: {}".format(err)))

    def get_inner_html_from_node(self, xpath: str) -> str:
        try:
            element = WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            return element.get_attribute('innerHTML')
        except Exception as err:
            self.check_throw(Error("ERROR: {}".format(err)))

    def get_outer_html_from_node(self, xpath: str) -> str:
        try:
            element = WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            return element.get_attribute('outerHTML')
        except Exception as err:
            self.check_throw(Error("ERROR: {}".format(err)))

    def check_node_for_property(self, xpath: str, property: str) -> bool:
        try:
            element = WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
            if element.get_property(property):
                return True
            else:
                return False
        except Exception as err:
            self.check_throw(Error("ERROR: {}".format(err)))

    def select_option_from_dropdown(self, xpath: str, select_type: DROPDOWNTYPE, value: Any) -> None:
        try:
            element = WebDriverWait(self.driver, self.poll_time, poll_frequency=self.poll_frequency).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
            select = Select(element)
            if select_type == DROPDOWNTYPE.INDEX:
                select.select_by_index(value)
            elif select_type == DROPDOWNTYPE.VALUE:
                select.select_by_value(value)
            elif select_type == DROPDOWNTYPE.TEXT:
                select.select_by_visible_text(value)
        except Exception as err:
            self.check_throw(Error("ERROR: {}".format(err)))
