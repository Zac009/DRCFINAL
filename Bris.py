import Jetson.GPIO as GPIO
import time
import sys
import numpy as np
import cv2

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Pins
SERVO_PIN = 33
ENA       = 32
IN1       = 12
IN2       = 11
IN3       = 7
IN4       = 13

# Constants
STEER_LEFT       = 7
STEER_CENTER     = 7.5
STEER_RIGHT      = 8
MIN_CONTOUR_AREA = 500

servo = None

def forward():
    GPIO.output(ENA, GPIO.HIGH)
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

def backward():
    GPIO.output(ENA, GPIO.HIGH)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

def steer_left():
    servo.ChangeDutyCycle(STEER_LEFT)

def steer_right():
    servo.ChangeDutyCycle(STEER_RIGHT)

def steer_center():
    servo.ChangeDutyCycle(STEER_CENTER)

def steer(pulse):
    servo.ChangeDutyCycle(pulse)

def stop():
    GPIO.output(ENA, GPIO.LOW)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    steer_center()


class Vision:
    def __init__(self):
        self.r_width  = 500
        self.r_height = 300
        self.direction = "Blue"

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

    def drive(self, action):
        if action == "forward":
            forward()
        elif action == "stop":
            stop()
        elif action == "corner":
            forward()

    def do_steer(self, pulse):
        steer(pulse)

    def main(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

        if not self.cap.isOpened():
            print("Cannot open camera")
            return

        ret, self.frame = self.cap.read()
        if not ret:
            print("Can't receive initial frame. Exiting ...")
            return

        steer_center()
        self.last_steer = STEER_CENTER
        self.last_drive = "forward"

        try:
            while True:
                ret, self.frame = self.cap.read()
                if not ret:                              # check ret BEFORE flip
                    print("Can't receive frame. Exiting ...")
                    break

                self.frame = cv2.flip(self.frame, -1)
                h, w = self.frame.shape[:2]
                self.frame = self.frame[:, w//2:]        # take right half
                self.height, self.width = self.frame.shape[:2]  # update after crop

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

                try:
                    if green_x is not None and self.width * 0.3 < green_x < self.width * 0.6:
                        print("Green - stopping")
                        self.drive("stop")
                        break
                    elif blue_x is not None and yellow_x is not None:
                        print("Straight")
                        center       = (blue_x + yellow_x) // 2
                        frame_center = self.width // 2
                        offset       = center - frame_center
                        if abs(offset) < 20:
                            self.do_steer(STEER_CENTER)
                            self.drive("forward")
                            self.last_steer = STEER_CENTER
                            self.last_drive = "forward"
                        elif offset > 0:
                            self.do_steer(STEER_RIGHT)
                            self.drive("corner")
                            self.last_steer = STEER_RIGHT
                            self.last_drive = "corner"
                        else:
                            self.do_steer(STEER_LEFT)
                            self.drive("corner")
                            self.last_steer = STEER_LEFT
                            self.last_drive = "corner"
                    elif blue_x is not None:
                        print("Only blue - steer left")
                        self.do_steer(STEER_LEFT)
                        self.drive("corner")
                        self.last_steer = STEER_LEFT
                        self.last_drive = "corner"
                    elif yellow_x is not None:
                        print("Only yellow - steer right")
                        self.do_steer(STEER_RIGHT)
                        self.drive("corner")
                        self.last_steer = STEER_RIGHT
                        self.last_drive = "corner"
                    else:
                        print("No lines - continuing last command")
                        self.do_steer(self.last_steer)
                        self.drive(self.last_drive)

                except Exception as e:
                    print("Steering error: {}".format(e))
                    self.drive("stop")
                    break

        except KeyboardInterrupt:
            print("Stopped by user")
        except Exception as e:
            print("Error: {}".format(e))
        finally:
            self.cap.release()
            cv2.destroyAllWindows()
            print("Done")


try:
    for pin in [SERVO_PIN, ENA, IN1, IN2, IN3, IN4]:
        GPIO.setup(pin, GPIO.OUT)

    servo = GPIO.PWM(SERVO_PIN, 50)
    servo.start(7.5)
    time.sleep(1)

    Ben = Vision()
    Ben.main()

finally:
    try:
        stop()
    except:
        pass
    if servo is not None:
        try:
            servo.stop()
        except:
            pass
    GPIO.cleanup()
    print("GPIO cleaned up")