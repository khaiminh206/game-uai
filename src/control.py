import math
import pyautogui

# Angle threshold (degrees) to trigger a key press
ANGLE_THRESHOLD = 15

# Current key state (avoids repeated press/release calls)
_current_key = None


def get_angle(red_point, blue_point):
    """
    Receives (x, y) coordinates of both color points.
    Returns the angle (in degrees) of the vector red -> blue
    relative to the horizontal axis.

    Screen coordinate system: Y increases downward
      dx = blue_x - red_x
      dy = blue_y - red_y

    angle = atan2(dy, dx):
      > 0  -> blue is lower than red  -> steering wheel turned RIGHT -> press ->
      < 0  -> blue is higher than red -> steering wheel turned LEFT  -> press <-

    Returns None if either point is missing.
    """
    if red_point is None or blue_point is None:
        return None

    dx = blue_point[0] - red_point[0]   # red -> blue vector (X axis)
    dy = blue_point[1] - red_point[1]   # red -> blue vector (Y axis, screen coords)

    angle = math.degrees(math.atan2(dy, dx))
    return angle


def get_direction(angle):
    """
    Receives an angle (degrees).
    Returns 'right', 'left', or 'straight'.

    angle > +THRESHOLD  -> turned right -> 'right'
    angle < -THRESHOLD  -> turned left  -> 'left'
    |angle| <= THRESHOLD -> straight    -> 'straight'
    """
    if angle is None:
        return 'straight'

    if angle > ANGLE_THRESHOLD:
        return 'right'
    elif angle < -ANGLE_THRESHOLD:
        return 'left'
    else:
        return 'straight'


def press_key(direction):
    """
    Receives a direction string, presses/releases the corresponding key.
    Only changes state when direction changes (avoids key spam).
    """
    global _current_key

    key_map = {
        'right':    'right',
        'left':     'left',
        'straight': None
    }

    new_key = key_map[direction]

    # No change -> do nothing
    if new_key == _current_key:
        return

    # Release previous key if held
    if _current_key is not None:
        pyautogui.keyUp(_current_key)

    # Press new key if applicable
    if new_key is not None:
        pyautogui.keyDown(new_key)

    _current_key = new_key


def release_all():
    """
    Releases all held keys. Call this when exiting the program.
    """
    global _current_key
    if _current_key is not None:
        pyautogui.keyUp(_current_key)
        _current_key = None