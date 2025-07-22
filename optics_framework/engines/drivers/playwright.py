
from typing import Any, Dict, Optional, Union
from playwright.sync_api import sync_playwright
from optics_framework.common.utils import SpecialKey, strip_sensitive_prefix
from optics_framework.common.driver_interface import DriverInterface
from optics_framework.common.config_handler import ConfigHandler
from optics_framework.common.logging_config import internal_logger
from optics_framework.common.eventSDK import EventSDK
from optics_framework.engines.drivers.playwright_driver_manager import set_playwright_driver
from optics_framework.engines.drivers.playwright_UI_helper import UIHelper


class PlaywrightDriver(DriverInterface):
    _instance = None
    DEPENDENCY_TYPE = "driver_sources"
    NAME = "playwright"
    ACTION_NOT_SUPPORTED = "Action not supported in Playwright."

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(PlaywrightDriver, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "initialized") and self.initialized:
            return
        self.driver: Optional[Any] = None
        config_handler = ConfigHandler.get_instance()
        config: Optional[Dict[str, Any]] = config_handler.get_dependency_config(
            self.DEPENDENCY_TYPE, self.NAME
        )
        if not config:
            internal_logger.error(
                f"No configuration found for {self.DEPENDENCY_TYPE}: {self.NAME}"
            )
            raise ValueError("Playwright driver not enabled in config")

        self.remote_url: str = config.get("url", "")

        self.capabilities = config.get("capabilities", {})
        if not self.capabilities:
            internal_logger.error("No capabilities found in config")
            raise ValueError("Playwright capabilities not found in config")
        all_caps = self.capabilities
        self.browser_url = all_caps.get("browserURL", "about:blank")
        self.browser_name = all_caps.get("browserName")

        self.eventSDK = EventSDK.get_instance()
        self.initialized = True
        self.ui_helper = None

    def start_session(self, event_name: str | None = None) -> Any:
        """Start a new Playwright session with the specified browser."""

        if not self.browser_name:
            raise ValueError("'browserName' capability is required.")

        browser_name = self.browser_name.lower()
        p = sync_playwright().start()

        try:
            if self.remote_url:
                internal_logger.info(f"Connecting to remote Playwright server at: {self.remote_url}")
                if browser_name == "chromium":
                    browser = p.chromium.connect(self.remote_url)
                elif browser_name == "firefox":
                    browser = p.firefox.connect(self.remote_url)
                elif browser_name == "webkit":
                    browser = p.webkit.connect(self.remote_url)
                else:
                    raise ValueError(f"Unsupported browser for remote connection: {browser_name}")
            else:
                internal_logger.info(f"Launching local Playwright browser: {browser_name}")
                if browser_name == "chromium":
                    browser = p.chromium.launch()
                elif browser_name == "firefox":
                    browser = p.firefox.launch()
                elif browser_name == "webkit":
                    browser = p.webkit.launch()
                else:
                    raise ValueError(f"Unsupported browser for local launch: {browser_name}")

            self.driver = browser.new_page()
            set_playwright_driver(self.driver)
            if event_name:
                internal_logger.debug(
                    f"Starting Playwright session with event: {event_name}")
                self.eventSDK.capture_event(event_name)
            self.ui_helper = UIHelper()
            internal_logger.debug(
                f"Started Playwright session with browser: {browser_name}")

        except Exception as e:
            internal_logger.error(f"Failed to start Playwright session: {e}")
            raise
        return self.driver

    def terminate(self, event_name: str | None = None) -> None:
        """End the current Playwright session."""
        if self.driver is not None:
            try:
                self.driver.close()
                internal_logger.debug("Playwright session ended")
                if event_name:
                    internal_logger.debug(
                        f"Ending Playwright session with event: {event_name}")
                    self.eventSDK.capture_event(event_name)
            except Exception as e:
                internal_logger.error(f"Failed to end Playwright session: {e}")
            finally:
                self.driver = None

    def launch_app(self, event_name: str | None = None) -> None:
        """Launch the web application by navigating to the browser URL."""
        if self.driver is None:
            self.start_session()
        if self.driver is None:
            internal_logger.error("Playwright driver is not initialized.")
            raise RuntimeError("Playwright driver is not initialized.")
        try:
            self.driver.goto(self.browser_url)
            if event_name:
                internal_logger.debug(
                    f"Launching app at {self.browser_url} with event: {event_name}")
                self.eventSDK.capture_event(event_name)
            internal_logger.debug(
                f"Launched web app at {self.browser_url} with event: {event_name}")
        except Exception as e:
            internal_logger.error(f"Failed to launch app at {self.browser_url}: {e}")
            raise

    def launch_other_app(self, app_name: str, event_name: str | None = None) -> None:
        """Launch another web application by navigating to the specified URL."""
        if self.driver is None:
            self.start_session()
        if self.driver is None:
            internal_logger.error("Playwright driver is not initialized.")
            raise RuntimeError("Playwright driver is not initialized.")
        try:
            # Here app_name is treated as a URL for Playwright
            self.driver.goto(app_name)
            if event_name:
                internal_logger.debug(
                    f"Launching other app at {app_name} with event: {event_name}")
                self.eventSDK.capture_event(event_name)
            internal_logger.debug(
                f"Launched other web app at {app_name} with event: {event_name}")
        except Exception as e:
            internal_logger.error(f"Failed to launch other app at {app_name}: {e}")
            raise

    def press_element(self, element, repeat: int = 1, event_name: str | None = None) -> None:
        try:
            timestamp = None
            for _ in range(repeat):
                timestamp = self.eventSDK.get_current_time_for_events()
                element.click()
            internal_logger.debug(
                f"Pressed element {repeat} times with event: {event_name}")
            if event_name and timestamp is not None:
                self.eventSDK.capture_event_with_time_input(event_name, timestamp)
        except Exception as e:
            internal_logger.error(f"Failed to press element: {e}")
            raise

    def get_app_version(self) -> str:
        raise NotImplementedError

    def press_coordinates(self, coor_x: int, coor_y: int, event_name: str | None = None) -> None:
        self.driver.mouse.click(coor_x, coor_y)

    def press_percentage_coordinates(self, percentage_x: float, percentage_y: float, repeat: int = 1, event_name: str | None = None) -> None:
        self._raise_action_not_supported()

    def enter_text(self, text: str, event_name: str | None = None) -> None:
        self.driver.keyboard.type(strip_sensitive_prefix(text))

    def enter_text_element(self, element, text: str, event_name: str | None = None) -> None:
        element.fill(strip_sensitive_prefix(text))

    def press_keycode(self, keycode: int, event_name: str | None = None) -> None:
        self.driver.keyboard.press(keycode)

    def enter_text_using_keyboard(self, input_value: Union[str, SpecialKey], event_name: Optional[str] = None):
        self.driver.keyboard.type(strip_sensitive_prefix(input_value))

    def clear_text(self, event_name: str | None = None) -> None:
        self._raise_action_not_supported()

    def clear_text_element(self, element, event_name: str | None = None) -> None:
        element.fill("")

    def swipe(self, x_coor: int, y_coor: int, direction: str, swipe_length: int, event_name: str | None = None) -> None:
        self._raise_action_not_supported()

    def swipe_percentage(self, x_percentage: float, y_percentage: float, direction: str, swipe_percentage: float, event_name: str | None = None) -> None:
        self._raise_action_not_supported()

    def swipe_element(self, element, direction: str, swipe_length: int, event_name: str | None = None) -> None:
        self._raise_action_not_supported()

    def scroll(self, direction: str, duration: int = 1000, event_name: str | None = None) -> None:
        if direction == "down":
            self.driver.evaluate("window.scrollBy(0, window.innerHeight)")
        elif direction == "up":
            self.driver.evaluate("window.scrollBy(0, -window.innerHeight)")

    def get_text_element(self, element) -> str:
        return element.inner_text()

    def _raise_action_not_supported(self) -> None:
        internal_logger.warning(self.ACTION_NOT_SUPPORTED)
        raise NotImplementedError(self.ACTION_NOT_SUPPORTED)
