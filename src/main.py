import sys
import cv2
import numpy as np
from color import get_masks
from tracking import get_points, draw_points
from control import get_angle, get_direction, press_key, release_all

# --- Configuration ---
# Default: 1 = USB camera, 0 = built-in camera
# Pass camera index as argument: python main.py 0
CAMERA_INDEX = int(sys.argv[1]) if len(sys.argv) > 1 else 1
SHOW_DEBUG = True      # show debug window
SHOW_MASK  = False     # show HSV mask window (for color calibration)


def draw_hud(frame, angle, direction):
    """
    Draws the HUD (Heads-Up Display) onto the frame:
      - Current angle value
      - Direction indicator (LEFT / STRAIGHT / RIGHT)
      - Angle bar
    """
    h, w = frame.shape[:2]

    # --- Semi-transparent HUD background ---
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 110), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

    # --- Angle text ---
    angle_text = f"Angle: {angle:+.1f} deg" if angle is not None else "Angle: N/A"
    cv2.putText(frame, angle_text, (20, 38),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    # --- Direction indicator ---
    color_map = {
        'left':     (0, 100, 255),   # orange
        'right':    (0, 255, 100),   # green
        'straight': (200, 200, 200), # light grey
    }
    arrow_map = {
        'left':     '<-- LEFT',
        'right':    'RIGHT -->',
        'straight': '  STRAIGHT',
    }
    dir_color = color_map[direction]
    dir_text  = arrow_map[direction]
    cv2.putText(frame, dir_text, (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, dir_color, 3)

    # --- Angle bar ---
    bar_x, bar_y, bar_w, bar_h = w // 2 - 150, 92, 300, 12
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (80, 80, 80), -1)

    # Center tick (0°)
    mid_x = bar_x + bar_w // 2
    cv2.line(frame, (mid_x, bar_y - 3), (mid_x, bar_y + bar_h + 3), (200, 200, 200), 1)

    # Angle pointer (±90° mapped to ±150px)
    if angle is not None:
        clamped  = max(-90, min(90, angle))
        offset   = int(clamped / 90 * (bar_w // 2))
        ptr_x    = mid_x + offset
        ptr_color = (0, 80, 255) if direction == 'right' else \
                    (255, 80, 0) if direction == 'left'  else (200, 200, 200)
        cv2.rectangle(frame,
                      (ptr_x - 4, bar_y - 2),
                      (ptr_x + 4, bar_y + bar_h + 2),
                      ptr_color, -1)

    return frame

import platform

def main():
    if platform.system() == "Windows":
        cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_MSMF)
    else:
        cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    if not cap.isOpened():
        print(f"Cannot open camera index {CAMERA_INDEX}!")
        return
    print(f"Camera {CAMERA_INDEX} opened OK "
          f"({int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x"
          f"{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))})")

    print("=== game-uai running ===")
    print("Press Q to quit")
    print("Press M to toggle mask view")
    print()
    print("Controls:")
    print("  Turn LEFT  (blue up,   red down) -> angle < -15 -> press LEFT  arrow")
    print("  Turn RIGHT (blue down, red up)   -> angle > +15 -> press RIGHT arrow")
    print("  Threshold: +-15 degrees")

    global SHOW_MASK

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Cannot read frame!")
                break

            # 1. Mirror frame horizontally (like a mirror)
            frame = cv2.flip(frame, 1)

            # 2. HSV detection -> binary masks
            red_mask, blue_mask = get_masks(frame)

            # 3. Find centroids of both color blobs
            red_point, blue_point = get_points(red_mask, blue_mask)

            # 4. Compute angle and send key press
            angle     = get_angle(red_point, blue_point)
            direction = get_direction(angle)
            press_key(direction)

            # 5. Render debug view
            if SHOW_DEBUG:
                debug_frame = draw_points(frame.copy(), red_point, blue_point)
                debug_frame = draw_hud(debug_frame, angle, direction)
                cv2.imshow("game-uai | press Q to quit", debug_frame)

            if SHOW_MASK:
                cv2.imshow("Red mask",  red_mask)
                cv2.imshow("Blue mask", blue_mask)

            # 6. Handle keyboard shortcuts
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('m'):
                SHOW_MASK = not SHOW_MASK
                if not SHOW_MASK:
                    cv2.destroyWindow("Red mask")
                    cv2.destroyWindow("Blue mask")

    finally:
        release_all()
        cap.release()
        cv2.destroyAllWindows()
        print("=== Exited ===")


if __name__ == "__main__":
    main()