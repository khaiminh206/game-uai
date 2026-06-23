import cv2
import numpy as np


def get_centroid(mask):
    """
    Receives a binary mask (0/255).
    Returns (x, y) of the centroid of the largest contour,
    or None if no contour is found.
    """
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    # Use the largest contour (ignore small noise)
    largest = max(contours, key=cv2.contourArea)

    # Filter out very small regions (residual noise)
    if cv2.contourArea(largest) < 500:
        return None

    # Compute centroid using image moments
    M = cv2.moments(largest)
    if M["m00"] == 0:
        return None

    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    return (cx, cy)


def get_points(red_mask, blue_mask):
    """
    Receives 2 masks from color.py.
    Returns (red_point, blue_point) — each is (x, y) or None.
    """
    red_point  = get_centroid(red_mask)
    blue_point = get_centroid(blue_mask)
    return red_point, blue_point


def draw_points(frame, red_point, blue_point):
    """
    Draws both points and the connecting line on the frame for debugging.
    Returns the annotated frame.
    """
    if red_point:
        cv2.circle(frame, red_point, 10, (0, 0, 255), -1)
        cv2.putText(frame, "RED", (red_point[0] + 12, red_point[1]),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    if blue_point:
        cv2.circle(frame, blue_point, 10, (255, 0, 0), -1)
        cv2.putText(frame, "BLUE", (blue_point[0] + 12, blue_point[1]),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    if red_point and blue_point:
        cv2.line(frame, red_point, blue_point, (0, 255, 0), 2)  # connecting line

    return frame