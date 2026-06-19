import time
import numpy as np
import cv2
import sys
import select
import os



def blue_det(frame_HSV):
    lower_blue = np.array([90, 50, 120])
    upper_blue = np.array([150, 255, 255])
    return cv2.inRange(frame_HSV, lower_blue, upper_blue)


def main():
    snapshot_counter = 0  # put this before the while loop
    cap = cv2.VideoCapture(0)  # 0 = default camera
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    print("Camera opened. Press 'q' to quit, 's' to save a snapshot.")

    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, -1)  # -1 = flip both horizontal and vertical
        if not ret:
            print("Error: Failed to grab frame.")
            break
        frame_HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        blue_mask     = blue_det(frame_HSV)
        roi_height    = frame.shape[0] // 4
        final_mask = blue_mask[-roi_height:, :]
        if select.select([sys.stdin], [], [], 0)[0]:
            key = sys.stdin.readline().strip()
            if key == "s":
                filename = "snapshot{}.jpg".format(snapshot_counter)
                cv2.imwrite(filename, final_mask)
                snapshot_counter += 1
                filename = "snapshot{}.jpg".format(snapshot_counter)
                cv2.imwrite(filename, frame)
                print("Snapshot saved to {}".format(filename))
                snapshot_counter += 2
    cap.release()

if __name__ == "__main__":
    main()
    