from typing import Any, Tuple
from optics_framework.common.elementsource_interface import ElementSourceInterface
from optics_framework.common.logging_config import internal_logger
from optics_framework.engines.drivers.playwright_driver_manager import get_playwright_driver
from optics_framework.engines.drivers.playwright_UI_helper import UIHelper
from optics_framework.common import utils
import time


class PlaywrightFindElement(ElementSourceInterface):
    """
    Playwright Find Element Class
    """

    def __init__(self):
        """
        Initialize the Playwright Find Element Class.
        """
        self.driver = None
        self.tree = None
        self.root = None


    def _get_playwright_driver(self):
        if self.driver is None:
            self.driver = get_playwright_driver()
        return self.driver

    def capture(self) -> None:
        """
        Capture the current screen state.
        """
        internal_logger.exception('Playwright Find Element does not support capturing the screen state.')
        raise NotImplementedError('Playwright Find Element does not support capturing the screen state.')

    def get_page_source(self) -> str:
        """
        Get the page source of the current page.
        """
        return UIHelper.get_page_source()

    def get_interactive_elements(self):

        internal_logger.exception("Getting interactive elements is not yet suppored using Playwright Find Element.")
        raise NotImplementedError(
            "Getting interactive elements is not yet suppored using Playwright Find Element."
        )

    def locate(self, element: str, index: int = None) -> Any:
        element_type = utils.determine_element_type(element)
        driver = self._get_playwright_driver()

        if index is not None:
            raise ValueError('Playwright Find Element does not support locating elements using index.')

        try:
            if element_type == "Image":
                internal_logger.debug("Playwright does not support locating elements by image.")
                return None

            elif element_type == "XPath":
                internal_logger.debug(f"Locating by XPath: {element}")
                return driver.locator(element)

            elif element_type == "Text":
                # Try various Playwright locators for text-based elements
                locators = [
                    lambda: driver.get_by_role("textbox", name=element),
                    lambda: driver.get_by_role("button", name=element),
                    lambda: driver.get_by_text(element),
                    lambda: driver.get_by_label(element),
                    lambda: driver.get_by_placeholder(element),
                    lambda: driver.get_by_alt_text(element),
                    lambda: driver.get_by_title(element),
                    lambda: driver.get_by_test_id(element)
                ]

                for locator_func in locators:
                    try:
                        located_element = locator_func()
                        # Check if the element is actually present/visible
                        if located_element.count() > 0:
                            internal_logger.debug(f"Located by {locator_func.__name__}: {element}")
                            return located_element
                    except Exception as e:
                        internal_logger.debug(f"Locator {locator_func.__name__} failed for '{element}': {e}")

                internal_logger.warning(f"Could not locate element using any Playwright strategy for: {element}")
                return None
        except Exception as e:
            internal_logger.error(f"Unexpected error locating element {element}: {e}")
            return None

    def _find_element_by_any(self, locator_value: str):
        driver = self._get_playwright_driver()
        try:
            return driver.locator(locator_value)
        except Exception:
            internal_logger.warning(f"No matching element found using any strategy for: {locator_value}")
            return None


    def assert_elements(self, elements, timeout=10, rule="any") -> Tuple[bool, str]:
        if rule not in ["any", "all"]:
            raise ValueError("Invalid rule. Use 'any' or 'all'.")

        if self.driver is None:
            raise RuntimeError(
                "Playwright session not started. Call start_session() first.")

        start_time = time.time()
        found_elements = []  # Initialize found_elements to avoid unbound error

        while time.time() - start_time < timeout:
            found_elements = [self.locate(
                element) is not None for element in elements]

            if (rule == "all" and all(found_elements)) or (rule == "any" and any(found_elements)):
                timestamp = utils.get_timestamp()
                internal_logger.debug(
                    f"Assertion passed with rule '{rule}' for elements: {elements}")
                return True,timestamp

            time.sleep(0.3)  # Polling interval
        raise TimeoutError(
            "Timeout reached: None of the specified elements were found.")


    def locate_using_index(self, element: Any, index: int) -> Tuple[int, int] | None:
        raise NotImplementedError(
            'Playwright Find Element does not support locating elements using index.')
