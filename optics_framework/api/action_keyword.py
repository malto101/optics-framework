from functools import wraps
from typing import Callable
from optics_framework.common.logging_config import logger, apply_logger_format_to_all
from optics_framework.common.optics_builder import OpticsBuilder
from optics_framework.common.strategies import StrategyManager
from optics_framework.common import utils
from .verifier import Verifier
import time

# Action Executor Decorator


def with_self_healing(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(self, element, *args, **kwargs):
        utils.capture_screenshot(func.__name__)
        results = self.strategy_manager.locate(element)

        last_exception = None
        for result in results:
            try:
                return func(self, element, located=result.value, *args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Action '{func.__name__}' failed with {result.strategy.__class__.__name__}: {e}")
                last_exception = e

        if last_exception:
            raise ValueError(
                f"All strategies failed for '{element}' in '{func.__name__}': {last_exception}")
    return wrapper


@apply_logger_format_to_all("internal")
class ActionKeyword:
    """
    High-Level API for Action Keywords

    This class provides functionality for managing action keywords related to applications,
    including pressing elements, scrolling, swiping, and text input.
    """
    SCREENSHOT_DISABLED_MSG = "Screenshot taking is disabled, not possible to locate element."
    XPAHT_NOT_SUPPORTED_MSG = "XPath is not supported for vision based search."

    def __init__(self, builder: OpticsBuilder):
        self.driver = builder.get_driver()
        self.element_source = builder.get_element_source()
        self.image_detection = builder.get_image_detection()
        self.text_detection = builder.get_text_detection()
        self.verifier = Verifier(builder)
        self.strategy_manager = StrategyManager(
            self.element_source, self.text_detection, self.image_detection)

    # Click actions
    @with_self_healing
    def press_element(
        self, element, repeat=1, offset_x=0, offset_y=0, event_name=None, *, located
    ):
        """
        Press a specified element.

        :param element: The element to be pressed (text, xpath or image).
        :param repeat: Number of times to repeat the press.
        :param offset_x: X offset of the press.
        :param offset_y: Y offset of the press.
        :param event_name: The event triggering the press.
        """
        if isinstance(located, tuple):
            x, y = located
            logger.debug(
                f"Pressing at coordinates ({x + offset_x}, {y + offset_y})")
            self.driver.press_coordinates(
                x + offset_x, y + offset_y, event_name)
        else:
            logger.debug(f"Pressing element '{element}'")
            self.driver.press_element(located, repeat, event_name)

    def press_by_percentage(self, percent_x, percent_y, repeat=1, event_name=None):
        """
        Press an element by percentage coordinates.

        :param percent_x: X percentage of the press.
        :param percent_y: Y percentage of the press.
        :param repeat: Number of times to repeat the press.
        :param event_name: The event triggering the press.
        """
        utils.capture_screenshot("press_by_percentage")
        element_source_type = type(
            self.element_source.current_instance).__name__
        if 'appium' in element_source_type.lower():
            self.driver.press_percentage_coordinates(
                percent_x, percent_y, repeat, event_name)
        else:
            # TODO: read device's screen specs from config
            # DUMMY IMPLEMENTATION
            screen_width = 1920
            screen_height = 1080
            x_coor = int(screen_width * percent_x)
            y_coor = int(screen_height * percent_y)
            self.driver.press_coordinates(x_coor, y_coor, event_name)

    def press_by_coordinates(self, coor_x, coor_y, repeat=1, event_name=None):
        """
        Press an element by absolute coordinates.

        :param coor_x: X coordinate of the press.
        :param coor_y: Y coordinate of the press.
        :param repeat: Number of times to repeat the press.
        :param event_name: The event triggering the press.
        """
        utils.capture_screenshot("press_by_coordinates")
        self.driver.press_coordinates(coor_x, coor_y, event_name)

    def press_element_with_index(self, element, index=0, event_name=None):
        """
        Press a specified text at a given index.

        :param element: The text or image to be pressed.
        :param index: The index of the element.
        :param event_name: The event triggering the press.
        """
        index = int(index)
        utils.capture_screenshot("press_element_with_index")
        element_source_type = type(
            self.element_source.current_instance).__name__
        element_type = utils.determine_element_type(element)
        if element_type == 'Text':
            if element_source_type == 'AppiumFindElement':
                logger.exception(
                    'Appium Find Element does not support finding text by index.')
            elif element_source_type == 'AppiumPageSource':
                appium_element = self.element_source.locate(
                    element, index)
                self.driver.press_element(
                    appium_element, repeat=1, event_name=event_name)
            else:
                if 'screenshot' not in element_source_type.lower():
                    logger.error(self.SCREENSHOT_DISABLED_MSG)
                screenshot_image = self.element_source.capture()
                x_coor, y_coor = self.text_detection.locate(
                    screenshot_image, element, index)
                self.driver.press_coordinates(
                    x_coor, y_coor, event_name=event_name)
        elif element_type == 'Image':
            if 'screenshot' not in element_source_type.lower():
                logger.error(self.SCREENSHOT_DISABLED_MSG)
            screenshot_image = self.element_source.capture()
            x_coor, y_coor = self.image_detection.locate(
                screenshot_image, element, index)
            self.driver.press_coordinates(
                x_coor, y_coor, event_name=event_name)
        elif element_type == 'XPath':
            logger.debug(
                'XPath is not supported for index based location. Provide the attribute as text.')

    @with_self_healing
    def detect_and_press(self, element, timeout, event_name=None, *, located):
        """
        Detect and press a specified element.

        :param element: The element to be detected and pressed (Image template, OCR template, or XPath).
        :param timeout: Timeout for the detection operation.
        :param event_name: The event triggering the press.
        """
        utils.capture_screenshot("detect_and_press")
        result = self.verifier.assert_presence(
            element, timeout=timeout, rule="any")
        if result:
            if isinstance(located, tuple):
                x, y = located
                logger.debug(
                    f"Pressing detected element at coordinates ({x}, {y})")
                self.driver.press_coordinates(
                    x, y, event_name=event_name)
            else:
                logger.debug(f"Pressing detected element '{element}'")
                self.driver.press_element(located, repeat=1, event_name=event_name)

    @DeprecationWarning
    @with_self_healing
    def press_checkbox(self, element, event_name=None, *, located):
        """
        Press a specified checkbox element.

        :param element: The checkbox element (Image template, OCR template, or XPath).
        :param event_name: The event triggering the press.
        """
        self.press_element(element, event_name=event_name, located=located)

    @DeprecationWarning
    @with_self_healing
    def press_radio_button(self, element, event_name=None, *, located):
        """
        Press a specified radio button.

        :param element: The radio button element (Image template, OCR template, or XPath).
        :param event_name: The event triggering the press.
        """
        self.press_element(element, event_name=event_name, located=located)

    def select_dropdown_option(self, element, option, event_name=None):
        """
        Select a specified dropdown option.

        :param element: The dropdown element (Image template, OCR template, or XPath).
        :param option: The option to be selected.
        :param event_name: The event triggering the selection.
        """
        pass

    # Swipe and Scroll actions
    def swipe(self, coor_x, coor_y, direction='right', swipe_length=50, event_name=None):
        """
        Perform a swipe action in a specified direction.

        :param coor_x: X coordinate of the swipe.
        :param coor_y: Y coordinate of the swipe.
        :param direction: The swipe direction (up, down, left, right).
        :param swipe_length: The length of the swipe.
        :param event_name: The event triggering the swipe.
        """
        utils.capture_screenshot("swipe")
        self.driver.swipe(coor_x, coor_y, direction, swipe_length, event_name)

    @DeprecationWarning
    def swipe_seekbar_to_right_android(self, element, event_name=None):
        """
        Swipe a seekbar to the right.

        :param element: The seekbar element (Image template, OCR template, or XPath).
        """
        utils.capture_screenshot("swipe_seekbar_to_right_android")
        self.driver.swipe_element(element, 'right', 50, event_name)

    def swipe_until_element_appears(self, element, direction, timeout, event_name=None):
        """
        Swipe in a specified direction until an element appears.

        :param element: The target element (Image template, OCR template, or XPath).
        :param direction: The swipe direction (up, down, left, right).
        :param timeout: Timeout until element search is performed.
        :param event_name: The event triggering the swipe.
        """
        utils.capture_screenshot("swipe_until_element_appears")
        start_time = time.time()
        while time.time() - start_time < int(timeout):
            result = self.verifier.assert_presence(
                element, timeout=3, rule="any")
            if result:
                break
            self.driver.swipe_percentage(10, 50, direction, 25, event_name)
            time.sleep(3)

    @with_self_healing
    def swipe_from_element(self, element, direction, swipe_length, event_name=None, *, located):
        """
        Perform a swipe action starting from a specified element.

        :param element: The element to swipe from (Image template, OCR template, or XPath).
        :type element: str
        :param direction: The swipe direction (up, down, left, right).
        :type direction: str
        :param swipe_length: The length of the swipe.
        :type swipe_length: int or float
        :param event_name: The event triggering the swipe.
        :type event_name: str
        """
        if isinstance(located, tuple):
            x, y = located
            logger.debug(f"Swiping from coordinates ({x}, {y})")
            self.driver.swipe(x, y, direction, swipe_length, event_name)
        else:
            logger.debug(f"Swiping from element '{element}'")
            self.driver.swipe_element(
                located, direction, swipe_length, event_name)

    def scroll(self, direction, event_name=None):
        """
        Perform a scroll action in a specified direction.

        :param direction: The scroll direction (up, down, left, right).
        :type direction: str
        :param event_name: The event triggering the scroll.
        :type event_name: str
        """
        utils.capture_screenshot("scroll")
        self.driver.scroll(direction, 1000, event_name)

    @with_self_healing
    def scroll_until_element_appears(self, element, direction, timeout, event_name=None, *, located):
        """
        Scroll in a specified direction until an element appears.

        :param element: The target element (Image template, OCR template, or XPath).
        :type element: str
        :param direction: The scroll direction (up, down, left, right).
        :type direction: str
        :param timeout: Timeout for the scroll operation.
        :type timeout: int or float
        :param event_name: The event triggering the scroll.
        :type event_name: str
        """
        utils.capture_screenshot("scroll_until_element_appears")
        start_time = time.time()
        while time.time() - start_time < int(timeout):
            result = self.verifier.assert_presence(element, timeout=3, rule="any")
            if result:
                break
            self.driver.scroll(direction,1000, event_name)
            time.sleep(3)

    @with_self_healing
    def scroll_from_element(self, element, direction, scroll_length, event_name, *, located):
        """
        Perform a scroll action starting from a specified element.

        :param element: The element to scroll from (Image template, OCR template, or XPath).
        :type element: str
        :param direction: The scroll direction (up, down, left, right).
        :type direction: str
        :param scroll_length: The length of the scroll.
        :type scroll_length: int or float
        :param event_name: The event triggering the scroll.
        :type event_name: str
        """
        utils.capture_screenshot("scroll_from_element")
        self.swipe_from_element(
            element, direction, scroll_length, event_name, located=located)

    # Text input actions
    @with_self_healing
    def enter_text(self, element, text, event_name=None, *, located):
        """
        Enter text into a specified element.

        :param element: The target element (Image template, OCR template, or XPath).
        :type element: str
        :param text: The text to be entered.
        :type text: str
        :param event_name: The event triggering the input.
        :type event_name: str
        """
        if isinstance(located, tuple):
            x, y = located
            logger.debug(f"Entering text '{text}' at coordinates ({x}, {y})")
            self.driver.press_coordinates(x, y, event_name=event_name)
            self.driver.enter_text(text, event_name)
        else:
            logger.debug(f"Entering text '{text}' into element '{element}'")
            self.driver.enter_text_element(located, text, event_name)

    @DeprecationWarning
    def enter_text_using_keyboard_android(self, text, event_name=None):
        """
        Enter text using the keyboard.

        :param text: The text to be entered.
        :type text: str
        :param event_name: The event triggering the input.
        :type event_name: str
        """
        utils.capture_screenshot("enter_text_using_keyboard_android")
        self.driver.enter_text_using_keyboard(text, event_name)

    @with_self_healing
    def enter_number(self, element, number, event_name=None, *, located):
        """
        Enter a specified number into an element.

        :param element: The target element (Image template, OCR template, or XPath).
        :type element: str
        :param number: The number to be entered.
        :type number: int or float
        :param event_name: The event triggering the input.
        :type event_name: str
        """
        utils.capture_screenshot("enter_number")
        self.enter_text(element, str(number), event_name, located=located)

    def press_keycode(self, keycode, event_name):
        """
        Press a specified keycode.

        :param keycode: The keycode to be pressed.
        :type keycode: int
        :param event_name: The event triggering the press.
        :type event_name: str
        """
        utils.capture_screenshot("press_keycode")
        self.driver.press_keycode(keycode, event_name)

    @with_self_healing
    def clear_element_text(self, element, event_name=None, *, located):
        """
        Clear text from a specified element.

        :param element: The target element (Image template, OCR template, or XPath).
        :type element: str
        :param event_name: The event triggering the action.
        :type event_name: str
        """
        if isinstance(located, tuple):
            x, y = located
            logger.debug(f"Clearing text at coordinates ({x}, {y})")
            self.driver.press_coordinates(
                x, y, event_name=event_name)
            self.driver.clear_text(event_name)
        else:
            logger.debug(f"Clearing text from element '{element}'")
            self.driver.clear_text_element(located, event_name)

    def get_text(self, element):
        """
        Get the text from a specified element.

        :param element: The target element (Image template, OCR template, or XPath).
        :type element: str
        :return: The text from the element.
        :rtype: str
        """
        utils.capture_screenshot("get_text")
        element_source_type = type(self.element_source.current_instance).__name__
        element_type = utils.determine_element_type(element)
        if element_type in ["Text", "XPath"]:
            if 'appium' in element_source_type.lower():
                element = self.element_source.locate(element)
                return self.driver.get_text_element(element)
            else:
                logger.error('Get Text is not supported for vision based search yet.')
        else:
            logger.error('Get Text is not supported for image based search yet.')

    def sleep(self, duration):
        """
        Sleep for a specified duration.

        :param duration: The duration of the sleep.
        :type duration: int or float
        """
        time.sleep(int(duration))
