# OpenCV-color-tracker

A real-time computer vision project built with **Python**, **OpenCV**, and **NumPy** that tracks a colored object (such as a red ball) using your built-in laptop camera, computes its pixel center `(cx, cy)`, measures offset from the center of the frame, and displays simulated pan/tilt turret movement cues.

No external webcam or physical servo motors are required to run and test the vision pipeline.

---

## How It Works

1. **Laptop Camera Capture:** Reads live video frames from the built-in camera (`cv2.VideoCapture(0)`) and mirrors the image horizontally (`cv2.flip`) so left/right movement feels natural on screen.
2. **Blur & BGR-to-HSV Conversion:** Applies a slight Gaussian blur to reduce camera noise, then converts the frame from **BGR** to **HSV (Hue, Saturation, Value)**. HSV separates color tint (`Hue`) from brightness/shadows (`Value`), making color detection more stable under changing room lighting.
3. **Color Masking (`cv2.inRange`):** Isolates red pixels into a black-and-white binary mask. Because red wraps around both ends of OpenCV's Hue range (`0–10` and `170–179`), two masks are combined using `cv2.bitwise_or`.
4. **Morphological Cleanup (`erode` & `dilate`):** Erodes small white background speckles and dilates the remaining object blob so it stays clean and solid.
5. **Contour & Centroid Detection:** Finds contours in the mask, selects the largest contour above `MIN_AREA`, and calculates its exact center `(cx, cy)` using image moments (`cv2.moments`).
6. **Pan/Tilt Offset Calculation:** Compares `(cx, cy)` against the frame center `(center_x, center_y)` to compute `err_x` and `err_y`, then shows whether a pan-tilt turret would pan left/right or tilt up/down (using a `DEADZONE` to prevent jitter).

---

## Project Structure

```text
color-tracking-turret/
├── tracker.py        # Main OpenCV color-tracking script
├── requirements.txt  # Python dependencies
├── .gitignore        # Ignored files (venv, cache, OS files)
└── README.md         # Project documentation
```

---

## Setup & Installation

### 1. Create and enter the project folder
```bash
mkdir color-tracking-turret
cd color-tracking-turret
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv venv
```

* **macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```
* **Windows (Command Prompt):**
  ```cmd
  venv\Scripts\activate.bat
  ```
* **Windows (PowerShell):**
  ```powershell
  venv\Scripts\Activate.ps1
  ```

### 3. Install dependencies
```bash
pip install opencv-python numpy
pip freeze > requirements.txt
```

---

## How to Run

1. Make sure your virtual environment is activated and camera permissions are enabled for your terminal or code editor.
2. Run the script:
   ```bash
   python tracker.py
   ```
3. Hold a red object (such as a red ball, cap, or cloth) in front of your laptop camera.
4. Press **`q`** inside the video window to quit.

---

## What You Will See on Screen

* **Laptop Camera Feed:** Shows a center crosshair, a green dot on the detected object's center `(cx, cy)`, a line connecting center to target, and live status text (`PAN LEFT`, `PAN RIGHT`, `TILT UP`, `TILT DOWN`, or `CENTERED`).
* **Red Mask:** Shows a black-and-white view of what the color filter detects—white for matching red areas and black for everything else.

---

## Future Improvements

* Add interactive OpenCV trackbars to tune HSV thresholds for different lighting or colors (blue, green, yellow).
* Connect `err_x` and `err_y` to a proportional (P/PD/PID) controller sending angles over Serial/GPIO to physical pan-tilt servos.
