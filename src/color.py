import cv2
import numpy as np

# --- HSV color ranges ---
# Note: Red in HSV is split into 2 ranges (around 0° and 180°)
RED_LOWER_1 = np.array([0, 120, 70])
RED_UPPER_1 = np.array([10, 255, 255])
RED_LOWER_2 = np.array([170, 120, 70])
RED_UPPER_2 = np.array([180, 255, 255])

# Dark blue
BLUE_LOWER = np.array([100, 150, 70])
BLUE_UPPER = np.array([130, 255, 255])


def get_masks(frame):
    """
    Receives a BGR frame from the camera.
    Returns (red_mask, blue_mask) — binary images (0/255).
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Red: merge 2 HSV ranges
    red_mask1 = cv2.inRange(hsv, RED_LOWER_1, RED_UPPER_1)
    red_mask2 = cv2.inRange(hsv, RED_LOWER_2, RED_UPPER_2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)

    # Dark blue
    blue_mask = cv2.inRange(hsv, BLUE_LOWER, BLUE_UPPER)

    # Noise removal: erode small regions, fill holes
    kernel = np.ones((5, 5), np.uint8)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)
    blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, kernel)
    blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_CLOSE, kernel)

    return red_mask, blue_mask