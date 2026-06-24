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

def yellow_det(frame_HSV):
    lower_yellow = np.array([22, 50, 100])
    upper_yellow = np.array([50, 255, 255])
    return cv2.inRange(frame_HSV, lower_yellow, upper_yellow)

def green_det(frame_HSV):
    lower_green = np.array([35, 100, 100])
    upper_green = np.array([85, 255, 255])
    return cv2.inRange(frame_HSV, lower_green, upper_green)


def main():
    snapshot_counter = 10  # put this before the while loop
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
        h, w = frame.shape[:2]
        frame = frame[:, w//2:]  
        start_row = h // 3
        end_row = 2 * h // 3
        frame_HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        blue_mask    = blue_det(frame_HSV)
        yellow_mask  = yellow_det(frame_HSV)
        green_mask   = green_det(frame_HSV)
        final_mask = cv2.bitwise_or(blue_mask, yellow_mask)
        final_mask = cv2.bitwise_or(final_mask, green_mask)
        final_mask = final_mask[start_row:end_row, :]
        if select.select([sys.stdin], [], [], 0)[0]:
            key = sys.stdin.readline().strip()
            if key == "s":
                filename = "snapshot{}.jpg".format(snapshot_counter)
                cv2.imwrite(filename, final_mask)
                snapshot_counter += 1
                filename = "snapshot{}.jpg".format(snapshot_counter)
                cv2.imwrite(filename, frame)
                print("Snapshot saved to {}".format(filename))
                snapshot_counter += 1
    cap.release()

if __name__ == "__main__":
    main()
    