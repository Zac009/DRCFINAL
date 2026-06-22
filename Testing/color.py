import numpy as np
import cv2
import Jetson.GPIO as GPIO

MIN_CONTOUR_AREA = 200

class Vision:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    def blue_det(self):
        lower_blue = np.array([90, 50, 120])
        upper_blue = np.array([150, 255, 255])
        return cv2.inRange(self.frame_HSV, lower_blue, upper_blue)

    def yellow_det(self):
        lower_yellow = np.array([15, 50, 100])
        upper_yellow = np.array([50, 255, 255])
        return cv2.inRange(self.frame_HSV, lower_yellow, upper_yellow)

    def green_det(self):
        lower_green = np.array([35, 100, 100])
        upper_green = np.array([85, 255, 255])
        return cv2.inRange(self.frame_HSV, lower_green, upper_green)

    def main(self):
        if not self.cap.isOpened():
            print("Cannot open camera")
            return

        ret, self.frame = self.cap.read()
        if not ret:
            print("Can't receive initial frame. Exiting ...")
            return

        self.height, self.width = self.frame.shape[:2]

        try:
            while True:
                ret, self.frame = self.cap.read()
                if not ret:
                    print("Can't receive frame (stream end?). Exiting ...")
                    break

                self.frame_HSV = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)

                blue_mask   = self.blue_det()
                yellow_mask = self.yellow_det()
                green_mask  = self.green_det()

                roi_height      = self.height // 4
                blue_mask_roi   = blue_mask[-roi_height:, :]
                yellow_mask_roi = yellow_mask[-roi_height:, :]
                green_mask_roi  = green_mask[-roi_height:, :]

                contours_blue,   _ = cv2.findContours(blue_mask_roi,   cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                contours_yellow, _ = cv2.findContours(yellow_mask_roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                contours_green,  _ = cv2.findContours(green_mask_roi,  cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                blue_x   = None
                yellow_x = None
                green_x  = None

                if contours_blue:
                    largest_blue = max(contours_blue, key=cv2.contourArea)
                    if cv2.contourArea(largest_blue) > MIN_CONTOUR_AREA:
                        M = cv2.moments(largest_blue)
                        if M["m00"] != 0:
                            blue_x = int(M["m10"] / M["m00"])

                if contours_yellow:
                    largest_yellow = max(contours_yellow, key=cv2.contourArea)
                    if cv2.contourArea(largest_yellow) > MIN_CONTOUR_AREA:
                        M = cv2.moments(largest_yellow)
                        if M["m00"] != 0:
                            yellow_x = int(M["m10"] / M["m00"])

                if contours_green:
                    largest_green = max(contours_green, key=cv2.contourArea)
                    if cv2.contourArea(largest_green) > MIN_CONTOUR_AREA:
                        M = cv2.moments(largest_green)
                        if M["m00"] != 0:
                            green_x = int(M["m10"] / M["m00"])

                # Print detections
                if blue_x is not None:
                    print(f"Blue detected at x={blue_x}")
                if yellow_x is not None:
                    print(f"Yellow detected at x={yellow_x}")
                if green_x is not None:
                    print(f"Green detected at x={green_x}")
                if blue_x is None and yellow_x is None and green_x is None:
                    print("No color detected")

        except KeyboardInterrupt:
            print("Stopped by user (Ctrl+C)")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.cap.release()
            cv2.destroyAllWindows()

Ben = Vision()
Ben.main()