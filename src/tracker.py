import cv2
import numpy as np

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

MIN_AREA = 500
DEADZONE = 25
kernel = np.ones((5, 5), np.uint8)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Unable to access laptop camera. Check camera permissions or try index 1.")
        break

    # Mirror view so moving an object left/right matches what you see on screen
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    center_x, center_y = w // 2, h // 2

    # 1. Blur & convert BGR to HSV
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # 2. Mask red (wraps around 0 and 179 in OpenCV HSV)
    mask_low = cv2.inRange(hsv, np.array([0, 120, 70]), np.array([10, 255, 255]))
    mask_high = cv2.inRange(hsv, np.array([170, 120, 70]), np.array([179, 255, 255]))
    mask = cv2.bitwise_or(mask_low, mask_high)

    # 3. Clean noise with erosion and dilation
    mask = cv2.erode(mask, kernel, iterations=2)
    mask = cv2.dilate(mask, kernel, iterations=2)

    # 4. Find largest contour and compute pixel center
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawMarker(frame, (center_x, center_y), (255, 255, 255), cv2.MARKER_CROSS, 20, 1)

    label = "Searching for red target..."
    if contours:
        largest = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest) > MIN_AREA:
            moments = cv2.moments(largest)
            if moments["m00"] > 0:
                cx = int(moments["m10"] / moments["m00"])
                cy = int(moments["m01"] / moments["m00"])
                err_x = cx - center_x
                err_y = cy - center_y

                cv2.circle(frame, (cx, cy), 8, (0, 255, 0), -1)
                cv2.line(frame, (center_x, center_y), (cx, cy), (0, 255, 255), 2)

                pan_dir = "PAN LEFT" if err_x < -DEADZONE else ("PAN RIGHT" if err_x > DEADZONE else "CENTERED X")
                tilt_dir = "TILT UP" if err_y < -DEADZONE else ("TILT DOWN" if err_y > DEADZONE else "CENTERED Y")
                label = f"Center: ({cx}, {cy}) | {pan_dir}, {tilt_dir}"

    cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.imshow("Laptop Camera Feed", frame)
    cv2.imshow("Red Mask", mask)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
