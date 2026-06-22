import Jetson.GPIO as GPIO
import time
import sys
import numpy as np
import cv2
from Artemis import Arrow_Detection

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
STEER_LEFT       = 7.3
STEER_CENTER     = 7.5
STEER_RIGHT      = 7.7
MIN_CONTOUR_AREA = 100

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
        self.arrow = Arrow_Detection()
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.r_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.r_height)

        if not self.cap.isOpened():
            print("Cannot open camera")
            return
        ret, self.frame = self.cap.read()
        if not ret:
            print("Can't receive initial frame. Exiting ...")
            return
        else:
            print("Camera opened successfully")

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
    
    def purple_det(self):
        lower_purple = np.array([120, 70, 70])
        upper_purple = np.array([160, 255, 255])
        return cv2.inRange(self.frame_HSV, lower_purple, upper_purple)
    
    def black_det(self):
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([180, 255, 50])
        return cv2.inRange(self.frame_HSV, lower_black, upper_black)
    
    def arrow_det(self):
        direction = self.arrow.runner(self.black_mask_roi)
        if direction is False:
            steer_right()
            self.last_steer = STEER_RIGHT
            forward()
            time.sleep(1)
        elif direction is True:
            steer_left()
            self.last_steer = STEER_LEFT
            forward()
            time.sleep(0.1)
    
    def invert(self):
        if self.last_steer == STEER_LEFT:
            steer_right()
            self.last_steer = STEER_RIGHT
        elif self.last_steer == STEER_RIGHT:
            steer_left()
            self.last_steer = STEER_LEFT
        if self.last_drive != "forward":
            forward()
        time.sleep(0.1)
    
    def main(self):
        try:
            steer_center()
            self.last_steer = STEER_CENTER
            self.last_drive = "forward"
            forward()
            while True:
                ret, self.frame = self.cap.read()
                if not ret:
                    print("Can't receive frame. Exiting ...")
                    break
                self.frame = cv2.flip(self.frame, -1)  # -1 = flip both horizontal and vertical
                self.height, self.width = self.frame.shape[:2]
                self.frame = self.frame[:, self.width//2:]        # take right half
                self.height, self.width = self.frame.shape[:2]
                self.frame_HSV = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
                
                blue_mask   = self.blue_det()
                yellow_mask = self.yellow_det()
                green_mask  = self.green_det()
                purple_mask = self.purple_det()
                black_mask = self.black_det()
                start_row = self.height // 3
                end_row = 2 * self.height // 3

                blue_mask_roi = blue_mask[start_row:end_row, :]
                yellow_mask_roi = yellow_mask[start_row:end_row, :]
                green_mask_roi = green_mask[start_row:end_row, :]
                purple_mask_roi = purple_mask[start_row:end_row, :]
                self.black_mask_roi = black_mask[start_row:end_row, :]

                contours_blue, _ = cv2.findContours(blue_mask_roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                contours_yellow, _ = cv2.findContours(yellow_mask_roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                contours_green, _ = cv2.findContours(green_mask_roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                contours_purple, _ = cv2.findContours(purple_mask_roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                contours_black, _ = cv2.findContours(self.black_mask_roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                blue_x = None
                yellow_x = None
                green_x = None
                purple_x = None 
                black_x = None

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

                if contours_purple:
                    largest_purple = max(contours_purple, key=cv2.contourArea)
                    if cv2.contourArea(largest_purple) > MIN_CONTOUR_AREA:
                        M = cv2.moments(largest_purple)
                        if M["m00"] != 0:
                            purple_x = int(M["m10"] / M["m00"])

                if contours_black:
                    largest_black = max(contours_black, key=cv2.contourArea)
                    if cv2.contourArea(largest_black) > MIN_CONTOUR_AREA:
                        M = cv2.moments(largest_black)
                        if M["m00"] != 0:
                            black_x = int(M["m10"] / M["m00"])

                try:
                    if green_x is not None and self.width * 0.3 < green_x < self.width * 0.6:
                        stop()
                        print("Stop line detected!!!")
                        break
                    elif black_x is not None:
                        self.arrow_det()
                    elif purple_x is not None:
                        self.invert()
                    elif blue_x is not None and yellow_x is not None:
                        steer_center()
                    elif blue_x is not None:
                        if self.last_steer != STEER_LEFT:    
                            steer(STEER_LEFT)
                        if self.last_drive != "forward":
                            forward()
                        self.last_steer = STEER_LEFT
                        self.last_drive = "forward"
                        time.sleep(0.1)
                    elif yellow_x is not None:
                        if self.last_steer != STEER_RIGHT:
                            steer(STEER_RIGHT)
                        if self.last_drive != "forward":
                            forward()
                        self.last_steer = STEER_RIGHT
                        self.last_drive = "forward"
                        time.sleep(0.1)
                    else:
                        time.sleep(0.1)
                        
                except Exception as e:
                    print("Error within the main loop: {}".format(e))
                    stop()
                    servo.stop()
                    break
        except KeyboardInterrupt:
            print("Stopped by user")
            stop()
            servo.stop()
            GPIO.cleanup()
            print("GPIO cleaned up")
        except Exception as e:
            print("Error: {}".format(e))
        finally:
            self.cap.release()
            print("Done")


try:
    for pin in [SERVO_PIN, ENA, IN1, IN2, IN3, IN4]:
        GPIO.setup(pin, GPIO.OUT)

    servo = GPIO.PWM(SERVO_PIN, 50)
    servo.start(7.5)
    time.sleep(1)

    Fred = Vision()
    print("The Mystery Machine is ready- Fred Jones \n")
    while True:
        if input() == 'x':
            Fred.main()
            break

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
    