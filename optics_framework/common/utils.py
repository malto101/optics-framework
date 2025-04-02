from datetime import datetime, timezone, timedelta
import hashlib
from fuzzywuzzy import fuzz
import re
import os
import cv2
import numpy as np
from optics_framework.common.logging_config import logger
from optics_framework.common.config_handler import ConfigHandler
from optics_framework.engines.elementsources.device_screenshot import DeviceScreenshot
from optics_framework.engines.elementsources.camera_screenshot import CameraScreenshot
from optics_framework.engines.elementsources.selenium_screenshot import SeleniumScreenshot


def determine_element_type(element):
    # Check if the input is an Image path
    if element.split(".")[-1] in ["jpg", "jpeg", "png", "bmp"]:
        return "Image"
    # Check if the input is an XPath
    if element.startswith("/") or element.startswith("//") or element.startswith("("):
        return "XPath"
    # Default case: consider the input as Text
    return "Text"


def get_current_time_for_events():
    try:
        current_utc_time = datetime.now(timezone.utc)
        desired_timezone = timezone(timedelta(hours=5, minutes=30))
        current_time_in_desired_timezone = current_utc_time.astimezone(desired_timezone)
        formatted_time = current_time_in_desired_timezone.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        return formatted_time[:-2] + ":" + formatted_time[-2:]
    except Exception as e:
        logger.error('Unable to get current time', exc_info=e)
        return None



def compute_hash(xml_string):
    """Computes the SHA-256 hash of the XML string."""
    return hashlib.sha256(xml_string.encode('utf-8')).hexdigest()


def compare_text(given_text, target_text):
    """
    Compare two text values using exact, partial, and fuzzy matching.
    Returns True if the texts match closely enough, otherwise False.
    """
    # Normalize both texts (case insensitive, strip whitespace)
    given_text = given_text.strip().lower()
    target_text = target_text.strip().lower()

    # Check if either of the strings is empty and return False if so
    if not given_text or not target_text:
        logger.debug(f"One or both texts are empty: given_text='{given_text}', target_text='{target_text}'")
        return False

    # 1. Exact Match (return immediately)
    if given_text == target_text:
        logger.debug(f"Exact match found: '{given_text}' == '{target_text}'")
        logger.debug(f'Exact match found for text: {given_text}')
        return True

    # 2. Partial Match (substring, return immediately)
    if target_text in given_text:
        logger.debug(f"Partial match found: '{target_text}' in '{given_text}'")
        logger.debug(f'Partial match found for text: {target_text}')
        return True

    # 3. Fuzzy Match (only if exact and partial checks fail)
    fuzzy_match_score = fuzz.ratio(given_text, target_text)
    logger.debug(f"Fuzzy match score for '{given_text}' and '{target_text}': {fuzzy_match_score}")
    if fuzzy_match_score >= 80:  # Threshold for "close enough"
        logger.debug(f"Fuzzy match found: score {fuzzy_match_score}")
        logger.debug(f"Fuzzy match found for text: {given_text}, matched text '{target_text}' with fuzzy score {fuzzy_match_score} ")
        return True

    # If no matches found, return False
    logger.debug(f"No match found for '{given_text}' and '{target_text}' using all matching algorithms.")
    return False


def save_screenshot(img, name, time_stamp = None):
    """
    Save the screenshot with a timestamp and keyword in the filename.
    """
    if img is None:
        logger.error("Image is empty. Cannot save screenshot.")
        return
    name = re.sub(r'[^a-zA-Z0-9\s_]', '', name)
    if time_stamp is None:
        time_stamp = str(datetime.now().astimezone().strftime('%Y-%m-%dT%H-%M-%S-%f'))
    base_dir = str(ConfigHandler.get_instance().get_project_path())
    output_dir = os.path.join(base_dir, "execution_output")
    os.makedirs(output_dir, exist_ok=True)
    screenshot_file_path = os.path.join(output_dir, f"{time_stamp}-{name}.jpg")
    try:
        cv2.imwrite(screenshot_file_path, img)
        logger.debug(f'Screenshot saved as : {time_stamp}-{name}.jpg')
        logger.debug(f"Screenshot saved to :{screenshot_file_path}")

    except Exception as e:
        logger.debug(f"Error writing screenshot to file : {e}")


def annotate(annotation_detail):
    screenshot,bboxes,screenshot_name = annotation_detail
    # Iterate over each bounding box and annotate it on the image
    for bbox in bboxes:
        if bbox is None or len(bbox) != 2:
            logger.debug(f"Invalid bounding box: {bbox}")
            continue

        top_left, bottom_right = bbox
        if top_left is None or bottom_right is None:
            logger.debug(f"Invalid coordinates in bounding box: {bbox}")
            continue

        # Draw a rectangle around the bounding box
        cv2.rectangle(screenshot, tuple(top_left), tuple(
            bottom_right), color=(0, 255, 0), thickness=3)
        logger.debug(f"Bounding box {top_left} to {bottom_right} annotated.")
    # Save the annotated screenshot
    logger.debug(f'annnotated image: {len(screenshot)}')
    save_screenshot(screenshot,screenshot_name)


def is_black_screen(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    average_colour = np.mean(gray_image)
    black_threshold = 10
    return average_colour < black_threshold



def annotate_element(frame, centre_coor, bbox):
    # Annotation: Draw the bounding box around the text
    cv2.rectangle(frame, bbox[0], bbox[1], (0, 255, 0), 2)

    # Draw a small circle at the center of the bounding box (optional)
    cv2.circle(frame, centre_coor, 5, (0, 0, 255), -1)
    return frame


def annotate_and_save(frame, element_status):
    """
    Draw bounding boxes on the frame for found elements and save the annotated image.

    Args:
        frame (numpy.ndarray): Image to annotate.
        element_status (dict): Dictionary containing found elements and their bounding boxes.
    """
    if frame is None:
        return

    # Annotate detected texts and images with GREEN color (no labels)
    for category, items in element_status.items():
        for item_name, status in items.items():
            if status["found"] and status["bbox"]:
                (x1, y1), (x2, y2) = status["bbox"]
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green for both text and images

    # Save annotated frame
    save_screenshot(frame, name="annotated_frame")


def save_page_source(tree, time_stamp):
    base_dir = str(ConfigHandler.get_instance().get_project_path())
    output_dir = os.path.join(base_dir, "execution_output")
    os.makedirs(output_dir, exist_ok=True)

    page_source_file_path = os.path.join(output_dir, "page_sources_log.xml")

    # Remove any XML declaration
    cleaned_tree = re.sub(r'<\?xml[^>]+\?>', '', tree, flags=re.IGNORECASE).strip()

    # Wrap in <entry> tag
    entry_block = f'\n  <entry timestamp="{time_stamp}">\n{cleaned_tree}\n  </entry>\n'

    if not os.path.exists(page_source_file_path):
        with open(page_source_file_path, 'w', encoding='utf-8') as f:
            f.write(f"<logs>\n{entry_block}</logs>\n")
        logger.debug(f"Created new page source log file with first entry at: {time_stamp}")
    else:
        with open(page_source_file_path, 'r+', encoding='utf-8') as f:
            content = f.read()
            if not content.strip().endswith("</logs>"):
                logger.error("Invalid log file: missing closing </logs> tag.")
                return

            f.seek(0)
            updated_content = content.strip()[:-7] + entry_block + "</logs>\n"
            f.write(updated_content)
        logger.debug(f"Page source appended at: {time_stamp}")

    logger.debug(f"Page source saved to: {page_source_file_path}")

def capture_screenshot(name=None):
    """
    Capture a screenshot using the DeviceScreenshot class.
    If the screenshot is None or a black screen, fall back to CameraScreenshot.
    """
    try:
        screenshot = SeleniumScreenshot().capture()
        save_screenshot(screenshot, name)
        return screenshot
    except Exception as e:
        logger.debug(f"Error capturing screenshot from Selenium: {e}")
        screenshot = None
    # If Selenium screenshot is None or a black screen, switch to DeviceScreenshot
    try:
        screenshot = DeviceScreenshot().capture()
    except Exception as e:
        logger.debug(f"Error capturing screenshot from device: {e}")
        screenshot = None  # Ensure screenshot is None if exception occurs

    # If device screenshot is None or a black screen, switch to CameraScreenshot
    if screenshot is None:
        logger.debug("Device screenshot returned None. Falling back to CameraScreenshot.")
        screenshot = CameraScreenshot().capture()
    elif is_black_screen(screenshot):
        logger.debug("Device screenshot is black. Falling back to CameraScreenshot.")
        screenshot = CameraScreenshot().capture()

    # Final check: if CameraScreenshot also fails, log and return None
    if screenshot is None or is_black_screen(screenshot):
        logger.error("Both DeviceScreenshot and CameraScreenshot returned None or a black screen.")
        return None
    if name is not None:
        save_screenshot(screenshot, name)

    return screenshot
