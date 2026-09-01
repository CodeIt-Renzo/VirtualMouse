VirtualMouse.exe
____________________________________________________________________________________________________________________________________________________________________________________________


Version - 1.0.0 (Early Access)
Author & Founder - Rudraniel Singh (aka. RunTimeRenzo)

____________________________________________________________________________________________________________________________________________________________________________________________

--> Got a hand sprain, a finger sprain, can't touch your mouse for some unwanted or hidden reasons?
--> Got a faulty mousepad, or even a faulty mouse, that won't let you work seamlessly?
--> Tons of reasons?

Well then!!, VirtualMouse is the perfect choice for you!!!


An application which makes your daily Computer-life easy by letting you not touch your mouse but still work with your cursor as free as a bird in a sky!!!


# 🖐️ Virtual Mouse

A computer-vision-based **virtual mouse** that allows you to control your computer using hand gestures through a laptop/webcam camera.

The project uses **MediaPipe Hand Landmarker** to track hand landmarks in real time and **OpenCV** to capture and process the camera feed.

Instead of physically moving a mouse, the user's **index finger controls the mouse pointer**.

---

## ✨ Exciting Features!!!

* 🖐️ Real-time hand tracking
* 🖱️ Index finger controls the mouse pointer
* 👌 Thumb + index pinch for left click
* ✋ Pinch-and-hold for drag
* 🤌 Thumb + index + middle finger gesture for right click
* 🎯 Full-screen cursor control
* 🧊 Pointer stabilization to reduce jitter
* ⚡ Adaptive cursor smoothing for better responsiveness
* 📷 Works with a standard webcam/laptop camera
* 🚀 Runs at approximately 30 FPS on the target system

---

## 🛠️ Technologies Used
_________________________________________________________
| Technology      | Purpose                             |
| --------------- | ----------------------------------- |
| Python 3.14.6   | Main programming language           |
| OpenCV 5.0.0    | Camera capture and image processing |
| MediaPipe 1.0.1 | Hand landmark detection             |
| PyAutoGUI       | Controlling the system mouse        |
| NumPy           | Numerical operations                |
_________________________________________________________

---

## 📁 Project Structure

```text
VirtualMouse/
│
├── main.py
├── README.md
├── requirements.txt
│
└── models/
    └── hand_landmarker.task
___________________________________________________________________________

[] Installation:-

1. Install the dependencies

Run:-

pip install opencv-python mediapipe pyautogui


2. Add the MediaPipe model

Place the MediaPipe hand landmarker model inside:


models/hand_landmarker.task

The folder structure looks like:

VirtualMouse/
│
├── main.py
│
└── models/
    └── hand_landmarker.task
3. And There you go!!!
_____________________________________________________________________________

[] Running the Project

Simply install the given VirtualMouse.exe application file.

The webcam window should open automatically.

Move your index finger in front of the camera to control the mouse pointer.

Press Q to exit the program.


# Gesture Controls

[] Move Cursor

Keep your index finger extended and move it around.

The position of the index fingertip determines the mouse pointer position.

[] Left Click

Perform a deliberate pinch:


OPEN
  ↓
THUMB + INDEX CLOSED
  ↓
OPEN


The click occurs when the fingers are opened again.

This prevents tiny accidental movements from immediately triggering a click.

---

[] Drag

Perform a pinch and hold it:

OPEN
  ↓
PINCH
  ↓
HOLD
  ↓
MOVE
  ↓
OPEN

The mouse button remains pressed while the pinch is held.


[] Right Click

Bring the thumb, index finger and middle finger together:

THUMB + INDEX + MIDDLE
          ↓
       PINCH
          ↓
        OPEN


This produces one right click.

The right mouse button is **not held** during the gesture.


[] Pointer Stabilization

Raw hand-landmark coordinates can contain small amounts of noise.

Because of this, directly converting the fingertip position into mouse coordinates can cause the pointer to jitter.

The project therefore uses:

* Dead-zone filtering
* Adaptive smoothing
* Edge locking
* Screen-coordinate clamping

### Adaptive smoothing:-

Slow hand movements receive more stabilization, while fast movements receive less smoothing. Although in further updates, optimization of the pointer and the hand movements will be included.

This provides a balance between:
-->Stability
-->Responsiveness 

[]Camera Mapping:-

The project uses an inner region of the camera frame as the control area

The control area is mapped to the entire screen, allowing the user to reach the edges of the display without placing the hand directly against the camera boundary.



[]How It Works:-

The processing pipeline is approximately:

```text
Webcam
   │
   ▼
OpenCV
   │
   ▼
Video Frame
   │
   ▼
MediaPipe Hand Landmarker
   │
   ▼
21 Hand Landmarks
   │
   ├───────────────┐
   │               │
   ▼               ▼
Index Position   Finger Distances
   │               │
   ▼               ▼
Cursor          Gesture Detection
Movement        │
                ├── Left Click
                ├── Drag
                └── Right Click
   │
   ▼
PyAutoGUI
   │
   ▼
Operating System Mouse
```

---

# 🔬 Gesture Detection

The project calculates distances between fingertips and normalizes them according to hand size.

For example:

```text
Thumb ↔ Index
```

is used to detect the left-click/drag gesture.

For right click:

```text
Thumb ↔ Index
Thumb ↔ Middle
```

are considered together.

Two thresholds are used for pinch detection:

```text
PINCH_CLOSE
PINCH_OPEN
```

This hysteresis prevents rapid switching between open and closed states caused by small tracking fluctuations.

---

# ⚡ Performance

The project uses MediaPipe's:

```text
LIVE_STREAM
```

running mode and asynchronous hand detection.

This allows camera processing and hand-landmark inference to work without unnecessarily blocking the main display loop.

On the development system, the project achieved approximately:

```text
30 FPS
```

after optimization.

---

# 🐛 Known Limitations

The project currently has some limitations:

* Hand tracking can become less reliable when most of the hand leaves the camera frame.
* Very fast movements near the camera boundary may reduce tracking accuracy.
* Lighting conditions can affect hand detection.
* Occlusion of fingers can cause incorrect gesture recognition.
* Different hand sizes may require different pinch thresholds.
* Camera quality and processing performance affect responsiveness.

---

# 🚀 Future Improvements!!!

Possible future versions may include:

* [ ] Scroll gesture
* [ ] Middle click
* [ ] Double-click gesture
* [ ] Custom gesture configuration
* [ ] Better fingertip tracking near camera edges
* [ ] Euro Filter for improved pointer stability.
* [ ] Automatic gesture calibration
* [ ] Multi-monitor support
* [ ] Adjustable sensitivity
* [ ] GUI settings panel
* [ ] Gesture visualization
* [ ] Better low-light tracking
* [ ] CPU/GPU performance optimization

---

# 📌 Version

Current version:

V1.0.0 - Early Access

---

# 👨‍💻 Author

**RunTimeRenzo(Rudraniel)**

Built as a computer-vision and human-computer-interaction project using Python.

---

## 📜 License

This project is intended for educational and experimental purposes.
