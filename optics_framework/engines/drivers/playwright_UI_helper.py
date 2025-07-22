from bs4 import BeautifulSoup
from lxml import html
from typing import Optional, Any
from optics_framework.common.logging_config import internal_logger
from optics_framework.common import utils
from optics_framework.engines.drivers.playwright_driver_manager import get_playwright_driver
from playwright.sync_api import ElementHandle


class UIHelper:
    def __init__(self):
        """
        Initialize
        """
        self.driver = None

    def _get_playwright_driver(self):
        if self.driver is None:
            self.driver = get_playwright_driver()
        return self.driver

    def get_page_source(self):
        """
        Fetch the current UI tree (page source) from the Appium driver.
        """
        time_stamp = utils.get_timestamp()
        driver = self._get_playwright_driver()
        page_source = driver.content()
        # Parse using BeautifulSoup
        soup = BeautifulSoup(page_source, 'lxml')
        prettified_html = soup.prettify()
        if not isinstance(prettified_html, str):
            prettified_html = str(prettified_html)
        utils.save_page_source_html(prettified_html, time_stamp)
        internal_logger.debug('\n\n========== PAGE SOURCE FETCHED ==========\n')
        internal_logger.debug(f'Page source fetched at: {time_stamp}')
        internal_logger.debug('\n==========================================\n')
        return page_source

    def find_html_element_by_text(self, text: str, index: Optional[int] = None) -> Any:
        """
        Finds an HTML element by its visible text content.
        """
        page_source = self.get_page_source()
        tree = html.fromstring(page_source)
        elements = tree.xpath(f'//*[contains(text(), "{text}")]')
        if not elements:
            raise ValueError(f"No element found with text: {text}")
        if index is not None and 0 <= index < len(elements):
            return elements[index]
        return elements[0]

    def find_html_element_by_xpath(self, xpath: str, index: Optional[int] = None) -> Any:
        """
        Finds an HTML element by its XPath.
        """
        page_source = self.get_page_source()
        tree = html.fromstring(page_source)
        elements = tree.xpath(xpath)
        if not elements:
            raise ValueError(f"No element found with XPath: {xpath}")
        if index is not None and 0 <= index < len(elements):
            return elements[index]
        return elements[0]

    def convert_to_playwright_element(self, lxml_element: Any) -> ElementHandle:
        """
        Converts an lxml element to a Playwright ElementHandle by finding it using its XPath.
        """
        driver = self._get_playwright_driver()
        xpath = driver.evaluate_handle("""
            (element) => {
                let path = '';
                for (; element && element.nodeType === 1; element = element.parentNode) {
                    let id = Array.from(element.parentNode.children).indexOf(element) + 1;
                    path = `/${element.tagName.toLowerCase()}[${id}]` + path;
                }
                return path;
            }
        """, lxml_element)
        return driver.locator(xpath.json_value())
