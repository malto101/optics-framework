from optics_framework.common.text_interface import TextInterface
import cv2
import numpy as np
from google.cloud import vision
from google.cloud.vision_v1 import ImageAnnotatorClient
import difflib


class GoogleVisionHelper(TextInterface):
    """
    Helper class for Optical Character Recognition (OCR) using EasyOCR.

    This class uses EasyOCR to detect text in images and optionally locate
    specific reference text.
    """

    def __init__(self, language: str = "en", fuzzy_threshold: float = 0.5):
        """Initialize helper and store language preference.

        fuzzy_threshold controls token-level similarity acceptance (0..1).
        """
        self.language = language
        self.fuzzy_threshold = float(fuzzy_threshold)

    def find_element(self, input_data, text, index=None):
        """
        Locate specific text in the input image.

        Returns None if not found, otherwise a tuple (found_bool, center, bounds).
        """
        frame = input_data
        if frame is None:
            return False, (None, None), None

        # convert to grayscale for OCR (Google Vision accepts color too; keeping parity)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, ocr_results = self.detect_text(gray_frame)

        matches = []

        # 1) Try whole-phrase match within single OCR result (case-insensitive)
        for (bbox, detected_text, _) in ocr_results:
            detected_text = (detected_text or "").strip()
            if text.lower() in detected_text.lower():
                try:
                    top_left = bbox[0]
                    bottom_right = bbox[2]
                except (IndexError, TypeError):
                    continue
                x, y = int(top_left[0]), int(top_left[1])
                w = int(bottom_right[0] - top_left[0])
                h = int(bottom_right[1] - top_left[1])
                center_x = x + w // 2
                center_y = y + h // 2
                matches.append(((center_x, center_y), (top_left, bottom_right)))

        # 2) If no single-result match, attempt multi-word matching across separate detections
        if not matches:
            words = [w.strip().lower() for w in text.split() if w.strip()]
            if len(words) > 1:
                chosen = []
                used_indices = set()
                for word in words:
                    for i, (bbox, detected_text, _) in enumerate(ocr_results):
                        if i in used_indices:
                            continue
                        candidate = (detected_text or "").lower()
                        # exact contains
                        if word in candidate:
                            chosen.append((bbox, detected_text))
                            used_indices.add(i)
                            break
                        # fuzzy: compare each token in candidate to the word
                        for token in candidate.split():
                            ratio = difflib.SequenceMatcher(None, word, token).ratio()
                            if ratio >= self.fuzzy_threshold:
                                chosen.append((bbox, detected_text))
                                used_indices.add(i)
                                break
                        # continue to next word (we don't require every word to be found)

                if chosen:
                    xs = []
                    ys = []
                    for (bbox, _) in chosen:
                        try:
                            tl = bbox[0]
                            br = bbox[2]
                        except (IndexError, TypeError, AttributeError):
                            continue
                        xs.extend([int(tl[0]), int(br[0])])
                        ys.extend([int(tl[1]), int(br[1])])

                    if xs and ys:
                        min_x, max_x = min(xs), max(xs)
                        min_y, max_y = min(ys), max(ys)
                        center_x = (min_x + max_x) // 2
                        center_y = (min_y + max_y) // 2
                        top_left = (min_x, min_y)
                        bottom_right = (max_x, max_y)
                        matches.append(((center_x, center_y), (top_left, bottom_right)))

        if not matches:
            return False, (None, None), None

        # index selection
        if index is not None:
            if 0 <= index < len(matches):
                selected_centre, selected_bbox = matches[index]
            else:
                return False, (None, None), None
        else:
            selected_centre, selected_bbox = matches[0]

        return True, selected_centre, selected_bbox


    def element_exist(self, input_data, reference_data):
        """
        Check whether reference_data (text) exists in input_data (frame).

        Returns the center (x,y) tuple when found, otherwise None to match the
        TextInterface contract.
        """
        result = self.find_element(input_data, reference_data)
        # support both legacy tuple and None
        if not result:
            return None
        if isinstance(result, tuple) and len(result) >= 3:
            found, centre, _ = result
            if found and centre and centre != (None, None):
                return centre
        return None


    def detect_text(self, input_data: np.ndarray):
        """
        Detects text in a given NumPy array using Google Vision API and returns standardized OCR format.

        Returns:
            Tuple[None, List[Tuple[bbox, text, confidence]]]
            bbox = List[Tuple[int, int]] with 4 points
        """
        frame = input_data
        if frame is None or not isinstance(frame, np.ndarray):
            raise ValueError("Invalid frame provided. Ensure it's a valid NumPy array.")

        _, encoded_image = cv2.imencode('.jpg', frame)
        image_bytes = encoded_image.tobytes()
        client = ImageAnnotatorClient()
        image = vision.Image(content=image_bytes)

        response = client.text_detection(image=image)
        texts = response.text_annotations

        results = []
        # full_text is usually provided as the first annotation
        full_text = ""
        if texts:
            try:
                full_text = texts[0].description or ""
            except Exception:
                full_text = ""

        for text in texts[1:]:  # Skip full block (index 0)
            text_str = text.description
            vertices = text.bounding_poly.vertices
            if len(vertices) >= 4:
                bbox = [(v.x, v.y) for v in vertices]
                results.append((bbox, text_str, None))  # None for confidence placeholder
            else:
                continue

        return full_text, results
