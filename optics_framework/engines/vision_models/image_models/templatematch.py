import cv2
import os
import numpy as np
from typing import Optional, List, Tuple
from optics_framework.common.image_interface import ImageInterface
from optics_framework.common.logging_config import logger
from optics_framework.common.config_handler import ConfigHandler

class TemplateMatchingHelper(ImageInterface):
    """
    Template matching helper that detects a reference image inside an input image.

    This class uses OpenCV's :func:`cv2.matchTemplate` function to locate instances
    of a template (reference image) within a larger image.
    """

    def detect(
        self, input_data: np.ndarray, reference_data: np.ndarray, threshold: float = 0.8
    ) -> Optional[List[Tuple[int, int, int, int]]]:
        """
        Detect occurrences of a reference image inside the input image.

        :param input_data: The input image as a NumPy array.
        :type input_data: np.ndarray
        :param reference_data: The template image as a NumPy array.
        :type reference_data: np.ndarray
        :param threshold: Matching threshold, defaults to 0.8.
        :type threshold: float, optional

        :return: A list of bounding boxes (x_min, y_min, x_max, y_max) where the
                 template was detected, or None if no matches are found.
        :rtype: Optional[List[Tuple[int, int, int, int]]]

        :raises ValueError: If either `input_data` or `reference_data` is None.
        """
        if input_data is None or reference_data is None:
            raise ValueError("Input image and template image cannot be None")

        input_gray = cv2.cvtColor(input_data, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(reference_data, cv2.COLOR_BGR2GRAY)

        match_result = cv2.matchTemplate(
            input_gray, template_gray, cv2.TM_CCOEFF_NORMED
        )
        locations = np.nonzero(match_result >= threshold)
        h, w = template_gray.shape[:2]

        if locations[0].size == 0:
            return None  # No match found
        boxes = [(x, y, x + w, y + h) for y, x in zip(*locations)]

        return boxes

    def load_template(self, element: str) -> np.ndarray:
        """
        Load a template image from the input_templates folder.

        :param element: The name of the template image file.
        :type element: str

        :return: The template image as a NumPy array.
        :rtype: np.ndarray

        :raises ValueError: If the project path is not set.
        """
        project_path = str(ConfigHandler.get_instance().get_project_path())

        templates_folder = os.path.join(project_path, "input_templates")
        template_path = os.path.join(templates_folder, element)
        template = cv2.imread(template_path)

        return template

    def locate(self, frame, element):
        # fetch template from folder
        template = self.load_template(element)
        # locate the image element
        found, coor, frame = self.find_element(frame, template)
        if found:
            return coor
        else:
            logger.exception(f'Failed to locate image template: {element}')
            raise Exception(f'Failed to locate image template: {element}')

    def locate_using_index(self, frame, element, index):
        # fetch template from folder
        template = self.load_template(element)
        # # locate the image element
        found, coor, frame = self.find_element_index(frame, template, index)
        if found:
            return coor
        else:
            logger.error(f'Failed to locate image template: {element}')
            raise Exception(f'Failed to locate image template: {element}')

    def find_element(
        self, frame, reference_data, offset=[0,0], confidence_level=0.85, min_inliers=10):
        """
        Match a template image within a single frame image using SIFT and FLANN-based matching.
        Additionally, locate the center pixel of the template in the frame.

        Parameters:
        - frame (np.array): Image data of the frame.
        - template (np.array): Image data of the template.
        - offset (list): Optional x and y offsets in pixels to adjust the center location.
        - confidence_level (float): Confidence level for the ratio test (default is 0.75).
        - min_inliers (int): Minimum number of inliers required to consider a match valid (default is 10).

        Returns:
        - bool: True if the template is found in the frame, False otherwise.
        - tuple: (x, y) coordinates of the center of the template in the frame or (None, None) if no match is found.
        - frame (np.array): The frame with the template bounding box and adjusted center dot annotated.
        """
        # Create SIFT object
        sift = cv2.SIFT_create()

        # Create FLANN object with parameters
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)

        if reference_data is None or frame is None:
            # logger.debug("Error: Cannot read the images.")
            return False, (None, None), None

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(reference_data, cv2.COLOR_BGR2GRAY)

        # Detect keypoints and descriptors for both images
        kp_frame, des_frame = sift.detectAndCompute(frame_gray, None)
        kp_template, des_template = sift.detectAndCompute(template_gray, None)

        if des_template is None or des_frame is None:
            return False, (None, None), frame

        try:
            matches = flann.knnMatch(des_template, des_frame, k=2)
        except cv2.error:
            return False, (None, None), frame

        # Apply ratio test to filter good matches
        good_matches = []
        for m, n in matches:
            if m.distance < confidence_level * n.distance:
                good_matches.append(m)

        if len(good_matches) < min_inliers:
            return False, (None, None), frame

        # If enough good matches are found, calculate homography
        src_pts = np.float32(
            [kp_template[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32(
            [kp_frame[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        if M is None:
            return False, (None, None), frame

        matches_mask = mask.ravel().tolist()

        # Check the number of inliers
        inliers = np.sum(matches_mask)
        if inliers < min_inliers:
            return False, (None, None), frame

        # Calculate the center of the template and find its position in the frame
        h, w = reference_data.shape[:2]
        center_template = np.float32([[w / 2, h / 2]]).reshape(-1, 1, 2)
        center_frame = cv2.perspectiveTransform(center_template, M)
        center_x, center_y = int(center_frame[0][0][0]), int(
            center_frame[0][0][1])

        # Apply the offset to the center position
        center_x += offset[0]
        center_y -= offset[1]

        # Draw bounding box around the matched template in the source image
        pts = np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)
        frame = cv2.polylines(
            frame, [np.int32(dst)], True, (0, 255, 0), 3, cv2.LINE_AA)

        # Draw a small circle at the center point
        cv2.circle(frame, (center_x, center_y), 5,
                   (0, 0, 255), -1)  # Red dot at the center
        # save annotated frame
        # logger.debug('saving annotated frame')
        return True, (center_x, center_y), frame


    def find_element_index(
        self,frame, reference_data, index, confidence_level=0.85, min_inliers=10
    ):
        """
        Match a template image within a single frame image using SIFT and FLANN-based matching.
        Returns the location of a specific match by index.

        Parameters:
        - frame (np.array): Image data of the frame.
        - reference_data (np.array): Image data of the template.
        - index (int): The index of the match to retrieve.
        - offset (list): Optional x and y offsets in pixels to adjust the center location.
        - confidence_level (float): Confidence level for the ratio test (default is 0.85).
        - min_inliers (int): Minimum number of inliers required to consider a match valid (default is 10).

        Returns:
        - Bool: True if the template is found in the frame, False otherwise.
        - tuple: (x, y) coordinates of the indexed match or (None, None) if out of bounds.
        - frame (np.array): The frame with all detected templates annotated.
        """
        sift = cv2.SIFT_create()
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)

        if reference_data is None or frame is None:
            return False,(None, None), None

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(reference_data, cv2.COLOR_BGR2GRAY)

        kp_frame, des_frame = sift.detectAndCompute(frame_gray, None)
        kp_template, des_template = sift.detectAndCompute(template_gray, None)

        if des_template is None or des_frame is None:
            return False,(None, None), frame

        try:
            matches = flann.knnMatch(des_template, des_frame, k=2)
        except cv2.error:
            return False, (None, None), frame

        good_matches = [m for m, n in matches if m.distance < confidence_level * n.distance]

        if len(good_matches) < min_inliers:
            return False, (None, None), frame

        src_pts = np.float32([kp_template[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp_frame[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        if M is None:
            return False, (None, None), frame

        matches_mask = mask.ravel().tolist()
        inliers = np.sum(matches_mask)
        if inliers < min_inliers:
            return False, (None, None), frame

        h, w = reference_data.shape[:2]
        centers = []
        for i in range(len(good_matches)):
            if matches_mask[i]:
                center_template = np.float32([[w / 2, h / 2]]).reshape(-1, 1, 2)
                center_frame = cv2.perspectiveTransform(center_template, M)
                center_x, center_y = int(center_frame[0][0][0]), int(center_frame[0][0][1])
                centers.append((center_x, center_y))

                # Draw bounding box around the matched template in the frame
                pts = np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
                dst = cv2.perspectiveTransform(pts, M)
                frame = cv2.polylines(frame, [np.int32(dst)], True, (0, 255, 0), 3, cv2.LINE_AA)

                # Draw a small circle at the center
                cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)

        # Return the requested index
        if 0 <= index < len(centers):
            return True, centers[index], frame
        return False, (None, None), frame


    def element_exist(self,frame, reference_data, offset=[0, 0], confidence_level=0.85, min_inliers=10):
        """
        Match a template image within a single frame image using SIFT and FLANN-based matching.
        Finds both the center of the template and its bounding box.

        Parameters:
        - frame (np.array): Image data of the frame.
        - reference_data (np.array): Image data of the template.
        - offset (list): Optional [x, y] offsets in pixels to adjust the center location.
        - confidence_level (float): Confidence level for the ratio test (default is 0.85).
        - min_inliers (int): Minimum number of inliers required to consider a match valid (default is 10).

        Returns:
        - bool: True if the template is found, False otherwise.
        - tuple: (x, y) coordinates of the center of the template in the frame or (None, None) if no match is found.
        - list: [(top-left), (bottom-right)] bounding box coordinates or None if no match is found.
        """

        # Create SIFT object
        sift = cv2.SIFT_create()

        # Create FLANN object with parameters
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)

        if reference_data is None or frame is None:
            # logger.debug("Error: Cannot read the images.")
            return False, (None, None), None

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(reference_data, cv2.COLOR_BGR2GRAY)

        # Detect keypoints and descriptors for both images
        kp_frame, des_frame = sift.detectAndCompute(frame_gray, None)
        kp_template, des_template = sift.detectAndCompute(template_gray, None)

        if des_template is None or des_frame is None:
            # logger.debug("Error: No descriptors found in template or frame.")
            return False, (None, None), None

        try:
            matches = flann.knnMatch(des_template, des_frame, k=2)
        except cv2.error as e:
            logger.debug(f"Error in FLANN matching: {e}")
            return False, (None, None), None

        # Apply Lowe's ratio test to filter good matches
        good_matches = [m for m, n in matches if m.distance < confidence_level * n.distance]

        if len(good_matches) < min_inliers:
            # logger.debug(f"Not enough good matches found: {len(good_matches)} (min required: {min_inliers})")
            return False, (None, None), None

        # Extract matched keypoints
        src_pts = np.float32([kp_template[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp_frame[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        # Compute homography matrix
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        if M is None:
            # logger.debug("Homography matrix computation failed.")
            return False, (None, None), None

        matches_mask = mask.ravel().tolist()
        inliers = np.sum(matches_mask)

        if inliers < min_inliers:
            # logger.debug(f"Not enough inliers: {inliers} (min required: {min_inliers})")
            return False, (None, None), None

        # Find center of the template in the frame
        h, w = reference_data.shape[:2]
        center_template = np.float32([[w / 2, h / 2]]).reshape(-1, 1, 2)
        center_frame = cv2.perspectiveTransform(center_template, M)
        center_x, center_y = int(center_frame[0][0][0]), int(center_frame[0][0][1])

        # Apply the offset to the center position
        center_x += offset[0]
        center_y -= offset[1]

        # Find bounding box corners
        bbox_pts = np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
        try:
            bbox_transformed = cv2.perspectiveTransform(bbox_pts, M)
            bbox_corners = [(int(pt[0][0]), int(pt[0][1])) for pt in bbox_transformed]
            top_left = bbox_corners[0]
            bottom_right = bbox_corners[2]
        except cv2.error as e:
            logger.debug(f"Error in perspective transformation: {e}")
            return False, (None, None), None

        # logger.debug(f"Template found at center: ({center_x}, {center_y}) with bbox: {top_left} -> {bottom_right}")

        return True, (center_x, center_y), [top_left, bottom_right]
