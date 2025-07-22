"""
Capture Screen Module for Playwright

This module provides a concrete implementation of `ElementSourceInterface`
that captures images from the screen using Playwright.
"""
from typing import Optional
import cv2
import numpy as np
from playwright.sync_api import Error as PlaywrightError
from optics_framework.common.elementsource_interface import ElementSourceInterface
from optics_framework.common.logging_config import internal_logger
from optics_framework.engines.drivers.playwright_driver_manager import get_playwright_driver


class PlaywrightScreenshot(ElementSourceInterface):
    """
    Capture screenshots of the screen using Playwright.
    """

    def __init__(self):
        """
        Initialize the screen capture utility with a Playwright driver.
        """
        self.driver = None

    def _get_playwright_driver(self):
        """
        Get the Playwright driver instance.

        Returns:
            Page: The Playwright page instance.
        """
        if self.driver is None:
            self.driver = get_playwright_driver()
        return self.driver

    def capture(self) -> np.ndarray:
        """
        Capture a screenshot of the screen using Playwright.

        Returns:
            Optional[np.ndarray]: The captured screen image as a NumPy array,
            or `None` if capture fails.
        """
        return self.capture_screenshot_as_numpy()

    def get_interactive_elements(self):
        internal_logger.exception("Playwright Screenshot does not support getting interactive elements.")
        raise NotImplementedError(
            "Playwright Screenshot does not support getting interactive elements."
        )

    def capture_screenshot_as_numpy(self) -> Optional[np.ndarray]:
        """
        Captures a screenshot using Playwright and returns it as a NumPy array.

        Returns:
            Optional[numpy.ndarray]: The captured screenshot as a NumPy array,
            or None if capture fails.
        """
        try:
            driver = self._get_playwright_driver()
            screenshot_bytes = driver.screenshot()

            # Convert to NumPy array
            numpy_image = np.frombuffer(screenshot_bytes, np.uint8)
            numpy_image = cv2.imdecode(numpy_image, cv2.IMREAD_COLOR)
            return numpy_image

        except PlaywrightError as se:
            internal_logger.warning(
                f"PlaywrightError: {se}. Using external camera.")
            return None
        except Exception as e:
            internal_logger.warning(
                f"Error capturing Playwright screenshot: {e}. Using external camera.")
            return None

    def assert_elements(self, elements, timeout=30, rule='any') -> None:
        """
        Placeholder for asserting elements (not implemented).
        """
        raise NotImplementedError(
            "PlaywrightScreenshot does not implement assert_elements.")

    def locate(self, element) -> tuple:
        """
        Placeholder for locating elements (not implemented).
        """
        internal_logger.exception(
            "PlaywrightScreenshot does not support locating elements.")
        raise NotImplementedError(
            "PlaywrightScreenshot does not support locate.")

    def locate_using_index(self, element, index) -> tuple:
        """
        Placeholder for locating elements by index (not implemented).
        """
        internal_logger.exception(
            "PlaywrightScreenshot does not support locating elements using index.")
        raise NotImplementedError(
            "PlaywrightScreenshot does not support locate_using_index.")
