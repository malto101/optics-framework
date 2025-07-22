from optics_framework.common.elementsource_interface import ElementSourceInterface
from optics_framework.engines.drivers.playwright_driver_manager import get_playwright_driver
from optics_framework.common.logging_config import internal_logger
from optics_framework.common import utils
from optics_framework.engines.drivers.playwright_UI_helper import UIHelper
from playwright.sync_api import ElementHandle
from typing import Tuple
import time


class PlaywrightPageSource(ElementSourceInterface):
    """
    Playwright Page Source Handler Class

    This class is responsible for retrieving and interacting with the page source
    using Playwright.
    """

    def __init__(self):
        """
        Initialize the Playwright Page Source Handler Class.
        """
        self.driver = None
        self.ui_helper = UIHelper()
        self.tree = None
        self.root = None

    def _get_playwright_driver(self):
        if self.driver is None:
            self.driver = get_playwright_driver()
        return self.driver

    def capture(self):
        """
        Capture the current screen state.

        Not Supported: This method is not implemented for Playwright Find Element.
        """
        internal_logger.exception('Playwright Find Element does not support capturing the screen state.')
        raise NotImplementedError(
            'Playwright Find Element does not support capturing the screen state.')

    def get_page_source(self) -> str:
        """
        Get the page source of the current page.

        Returns:
            str: The raw page source.
        """
        return self.ui_helper.get_page_source()

    def get_interactive_elements(self):
        internal_logger.exception("Getting interactive elements is not yet suppored using Playwright Page Source.")
        raise NotImplementedError(
            "Getting interactive elements is not yet suppored using Playwright Page Source."
        )

    def locate(self, element: str, index: int = None) -> ElementHandle:
        """
        Locates a Playwright ElementHandle using either text or XPath from the current page source.
        """
        element_type = utils.determine_element_type(element)

        try:
            if element_type == 'Image':
                internal_logger.debug('Playwright does not support finding elements by image.')
                return None

            elif element_type == 'Text':
                match = self.ui_helper.find_html_element_by_text(element, index)
                element = self.ui_helper.convert_to_playwright_element(match)
                internal_logger.debug(f"Text-based element match found: {match},{element}")
                return element

            elif element_type == 'XPath':
                match = self.ui_helper.find_html_element_by_xpath(element, index)
                element = self.ui_helper.convert_to_playwright_element(match)
                internal_logger.debug(f"XPath-based element match found: {match},{element}")
                return element

            else:
                internal_logger.warning(f"Unsupported element type detected: {element_type}")
                return None

        except Exception as e:
            internal_logger.exception(f"Error locating element '{element}': {e}")
            raise Exception(f"Error locating element '{element}': {e}")

    def locate_using_index(self, element, index: int=None) -> dict:
        return self.locate(element, index)

    def assert_elements(self, elements: list, timeout: int = 30, rule: str = 'any') -> Tuple[bool, str]:
        """
        Assert the presence of elements in the page source (text or xpath based).
        """
        if rule not in {"any", "all"}:
            raise ValueError("Invalid rule. Use 'any' or 'all'.")

        start_time = time.time()
        texts = [el for el in elements if utils.determine_element_type(el) == 'Text']
        xpaths = [el for el in elements if utils.determine_element_type(el) == 'XPath']

        while time.time() - start_time < timeout:
            found_texts = [text for text in texts if self._is_text_found(text)]
            found_xpaths = [xpath for xpath in xpaths if self._is_xpath_found(xpath)]

            if (rule == "any" and (found_texts or found_xpaths)) or \
            (rule == "all" and len(found_texts) == len(texts) and len(found_xpaths) == len(xpaths)):
                timestamp = utils.get_timestamp()
                internal_logger.debug(f"Elements found with rule '{rule}' at {timestamp}")
                return True, timestamp

        missing_texts = list(set(texts) - set(found_texts))
        missing_xpaths = list(set(xpaths) - set(found_xpaths))
        internal_logger.warning(f"Timeout reached: Missing texts: {missing_texts}, Missing xpaths: {missing_xpaths}")
        raise TimeoutError(
            f"Timeout reached: Not all elements were found.\n"
            f"Missing texts: {missing_texts}\nMissing xpaths: {missing_xpaths}"
        )

    def _is_text_found(self, text: str) -> bool:
        try:
            self.ui_helper.find_html_element_by_text(text)
            return True
        except ValueError:
            return False

    def _is_xpath_found(self, xpath: str) -> bool:
        try:
            self.ui_helper.find_html_element_by_xpath(xpath)
            return True
        except ValueError:
            return False
