import cv2
import mediapipe as mp
import pyautogui
import time
import os
import threading
import math
import sys

# ============================================================
# SETTINGS
# ============================================================

if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))



MODEL_PATH = os.path.join(BASE_DIR, "models", "hand_landmarker.task")

CAMERA_INDEX = 0

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480


# Cursor responsiveness
SMOOTHING = 0.85


# ============================================================
# PINCH SETTINGS
# ============================================================

# Smaller = fingers must be closer
PINCH_CLOSE = 0.18

# Larger = fingers must move apart this far to release
PINCH_OPEN = 0.30


# ============================================================
# DRAG SETTINGS
# ============================================================

DRAG_DELAY = 0.15


# ============================================================
# CLICK SETTINGS
# ============================================================

CLICK_COOLDOWN = 0.40
RIGHT_CLICK_COOLDOWN = 0.50


# ============================================================
# SCREEN
# ============================================================

SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

print(
    f"Screen: {SCREEN_WIDTH} x {SCREEN_HEIGHT}"
)


# ============================================================
# SHARED MEDIAPIPE DATA
# ============================================================

latest_x = None
latest_y = None
latest_hand = None

hand_detected = False

data_lock = threading.Lock()


# ============================================================
# MEDIAPIPE CALLBACK
# ============================================================

def on_result(result, output_image, timestamp_ms):

    global latest_x
    global latest_y
    global latest_hand
    global hand_detected

    with data_lock:

        if result.hand_landmarks:

            hand = result.hand_landmarks[0]

            latest_hand = hand

            index = hand[8]

            latest_x = index.x
            latest_y = index.y

            hand_detected = True

        else:

            hand_detected = False


# ============================================================
# DISTANCE
# ============================================================

def distance(point1, point2):

    dx = point1.x - point2.x
    dy = point1.y - point2.y

    return math.sqrt(
        dx * dx +
        dy * dy
    )


# ============================================================
# MEDIAPIPE
# ============================================================

BaseOptions = mp.tasks.BaseOptions

HandLandmarker = (
    mp.tasks.vision.HandLandmarker
)

HandLandmarkerOptions = (
    mp.tasks.vision.HandLandmarkerOptions
)

RunningMode = (
    mp.tasks.vision.RunningMode
)


options = HandLandmarkerOptions(

    base_options=BaseOptions(
        model_asset_path=MODEL_PATH
    ),

    running_mode=RunningMode.LIVE_STREAM,

    num_hands=1,

    min_hand_detection_confidence=0.5,

    min_hand_presence_confidence=0.5,

    min_tracking_confidence=0.5,

    result_callback=on_result
)


# ============================================================
# CAMERA
# ============================================================

cap = cv2.VideoCapture(
    CAMERA_INDEX
)

if not cap.isOpened():

    print(
        "ERROR: Could not open camera."
    )

    exit()


cap.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    CAMERA_WIDTH
)

cap.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    CAMERA_HEIGHT
)


# ============================================================
# CURSOR
# ============================================================

cursor_x = SCREEN_WIDTH / 2
cursor_y = SCREEN_HEIGHT / 2


# ============================================================
# LEFT GESTURE STATE
# ============================================================

left_state = "OPEN"

left_pinch_start = 0

dragging = False


# ============================================================
# RIGHT GESTURE STATE
# ============================================================

right_state = "OPEN"

last_right_click = 0


# ============================================================
# LEFT CLICK COOLDOWN
# ============================================================

last_left_click = 0


# ============================================================
# TIMESTAMP
# ============================================================

timestamp_ms = 0


# ============================================================
# FPS
# ============================================================

previous_time = time.time()

fps = 0


# ============================================================
# MAIN LOOP
# ============================================================

with HandLandmarker.create_from_options(
    options
) as landmarker:

    while True:

        # ====================================================
        # CAMERA
        # ====================================================

        success, frame = cap.read()

        if not success:

            print(
                "ERROR: Camera frame failed."
            )

            break


        # Mirror

        frame = cv2.flip(
            frame,
            1
        )

        height, width, _ = frame.shape


        # ====================================================
        # MEDIAPIPE IMAGE
        # ====================================================

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )


        # ====================================================
        # ASYNC DETECTION
        # ====================================================

        timestamp_ms = (
            time.time_ns()
            // 1_000_000
        )

        landmarker.detect_async(
            mp_image,
            timestamp_ms
        )


        # ====================================================
        # COPY RESULT
        # ====================================================

        with data_lock:

            x = latest_x
            y = latest_y

            hand = latest_hand

            detected = hand_detected


        # ====================================================
        # HAND DETECTED
        # ====================================================

        if detected and hand is not None:

            # =================================================
            # LANDMARKS
            # =================================================

            thumb = hand[4]

            index = hand[8]

            middle = hand[12]

            wrist = hand[0]

            middle_mcp = hand[9]


            # =================================================
            # HAND SIZE
            # =================================================

            hand_size = distance(
                wrist,
                middle_mcp
            )


            if hand_size > 0:

                thumb_index = (
                    distance(
                        thumb,
                        index
                    )
                    / hand_size
                )

                thumb_middle = (
                    distance(
                        thumb,
                        middle
                    )
                    / hand_size
                )

            else:

                thumb_index = 999
                thumb_middle = 999


            # =================================================
            # GESTURE CONDITIONS
            # =================================================

            left_closed = (
                thumb_index
                < PINCH_CLOSE
            )


            left_open = (
                thumb_index
                > PINCH_OPEN
            )


            right_closed = (
                thumb_index
                < PINCH_CLOSE
                and
                thumb_middle
                < PINCH_CLOSE
            )


            right_open = (
                thumb_index
                > PINCH_OPEN
                and
                thumb_middle
                > PINCH_OPEN
            )


            # =================================================
            # RIGHT CLICK STATE MACHINE
            # =================================================

            if right_state == "OPEN":

                if right_closed:

                    right_state = "CLOSED"


            elif right_state == "CLOSED":

                # Wait until fingers actually open

                if right_open:

                    current_time = time.time()

                    if (
                        current_time
                        - last_right_click
                        > RIGHT_CLICK_COOLDOWN
                    ):

                        pyautogui.click(
                            button="right"
                        )

                        last_right_click = (
                            current_time
                        )

                    right_state = "OPEN"


            # =================================================
            # LEFT CLICK / DRAG
            # =================================================

            # Only process left gesture when
            # right gesture isn't active.

            if right_state == "OPEN":

                # ------------------------------------------------
                # OPEN → CLOSED
                # ------------------------------------------------

                if left_state == "OPEN":

                    if left_closed:

                        left_state = "CLOSED"

                        left_pinch_start = (
                            time.time()
                        )


                # ------------------------------------------------
                # CLOSED
                # ------------------------------------------------

                elif left_state == "CLOSED":

                    # How long have we been pinched?

                    pinch_time = (
                        time.time()
                        - left_pinch_start
                    )


                    # --------------------------------------------
                    # START DRAG
                    # --------------------------------------------

                    if (
                        pinch_time
                        >= DRAG_DELAY
                        and
                        not dragging
                    ):

                        dragging = True

                        pyautogui.mouseDown(
                            button="left"
                        )


                    # --------------------------------------------
                    # RELEASE
                    # --------------------------------------------

                    if left_open:

                        # End drag

                        if dragging:

                            pyautogui.mouseUp(
                                button="left"
                            )

                            dragging = False


                        # Quick pinch = click

                        else:

                            current_time = (
                                time.time()
                            )

                            if (
                                current_time
                                - last_left_click
                                > CLICK_COOLDOWN
                            ):

                                pyautogui.click(
                                    button="left"
                                )

                                last_left_click = (
                                    current_time
                                )


                        left_state = "OPEN"


            # =================================================
            # CURSOR MOVEMENT
            # =================================================

            target_x = (
                x * SCREEN_WIDTH
            )

            target_y = (
                y * SCREEN_HEIGHT
            )


            cursor_x += (
                target_x
                - cursor_x
            ) * SMOOTHING


            cursor_y += (
                target_y
                - cursor_y
            ) * SMOOTHING


            pyautogui.moveTo(
                int(cursor_x),
                int(cursor_y),
                _pause=False
            )


            # =================================================
            # DRAW INDEX
            # =================================================

            fingertip_x = int(
                index.x * width
            )

            fingertip_y = int(
                index.y * height
            )


            cv2.circle(
                frame,
                (
                    fingertip_x,
                    fingertip_y
                ),
                10,
                (0, 0, 255),
                -1
            )


            # =================================================
            # STATUS
            # =================================================

            if dragging:

                status = "DRAGGING"

            elif right_state == "CLOSED":

                status = "RIGHT PINCH"

            elif left_state == "CLOSED":

                status = "LEFT PINCH"

            else:

                status = "MOVE"


            cv2.putText(
                frame,
                status,
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )


            # =================================================
            # DEBUG
            # =================================================

            cv2.putText(
                frame,
                f"T-I: {thumb_index:.3f}",
                (10, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2
            )


            cv2.putText(
                frame,
                f"T-M: {thumb_middle:.3f}",
                (10, 105),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2
            )


        # ====================================================
        # HAND LOST
        # ====================================================

        else:

            cv2.putText(
                frame,
                "HAND NOT DETECTED",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )


            # Safety release

            if dragging:

                pyautogui.mouseUp(
                    button="left"
                )

                dragging = False


            left_state = "OPEN"

            right_state = "OPEN"


        # ====================================================
        # FPS
        # ====================================================

        current_time = time.time()

        elapsed = (
            current_time
            - previous_time
        )

        if elapsed > 0:

            fps = (
                0.9 * fps
                +
                0.1 * (1 / elapsed)
            )

        previous_time = current_time


        cv2.putText(
            frame,
            f"FPS: {int(fps)}",
            (10, 135),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )


        # ====================================================
        # DISPLAY
        # ====================================================

        cv2.imshow(
            "Virtual Mouse V0.3.2",
            frame
        )


        # ====================================================
        # QUIT
        # ====================================================

        if cv2.waitKey(1) & 0xFF == ord("q"):

            break


# ============================================================
# SAFETY CLEANUP
# ============================================================

if dragging:

    pyautogui.mouseUp(
        button="left"
    )


cap.release()

cv2.destroyAllWindows()