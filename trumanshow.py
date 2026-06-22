import Jetson.GPIO as GPIO
import time
import numpy as np
import cv2

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Pins
SERVO_PIN = 33
ENA       = 32
IN1       = 11
IN2       = 12
IN3       = 7
IN4       = 13

STEER_LEFT       = 8
STEER_CENTER     = 7.5
STEER_RIGHT      = 7
MIN_CONTOUR_AREA = 300

servo = None

def forward():
    GPIO.output(ENA, GPIO.HIGH)
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

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

class Vision:
    def __init__(self):
        pass

    def blue_det(self):
        lower_blue = np.array([90, 50, 120])
        upper_blue = np.array([150, 255, 255])
        return cv2.inRange(self.frame_HSV, lower_blue, upper_blue)

    def do_steer(self, pulse):
        steer(pulse)

    def main(self):
        print("Opening camera...")
        snapshotcounter = 0
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

        self.height, self.width = self.frame.shape[:2]
        self.last_steer = STEER_CENTER

        try:
            while True:
                ret, self.frame = self.cap.read()
                if not ret:
                    break

                self.frame_HSV = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)

                blue_mask     = self.blue_det()
                roi_height    = self.height // 4
                blue_mask_roi = blue_mask[-roi_height:, :]

                contours_blue, _ = cv2.findContours(blue_mask_roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                blue_x = None
                if contours_blue:
                    largest_blue = max(contours_blue, key=cv2.contourArea)
                    if cv2.contourArea(largest_blue) > MIN_CONTOUR_AREA:
                        M = cv2.moments(largest_blue)
                        if M["m00"] != 0:
                            blue_x = int(M["m10"] / M["m00"])

                if blue_x is not None:
                    frame_center = self.width // 2
                    offset       = blue_x - frame_center
                    print("Blue at x={} offset={}".format(blue_x, offset))
                    if snapshotcounter < 7:
                        filename = "snapshot{}.jpg".format(snapshotcounter)
                        cv2.imwrite(filename, blue_mask_roi)
                        snapshot_counter += 1
                        filename = "snapshot{}.jpg".format(snapshotcounter)
                        cv2.imwrite(filename, self.frame)
                        print("Snapshot saved")
                        snapshot_counter += 1
                    new_steer = STEER_CENTER
                    if abs(offset) < 20:
                        new_steer = STEER_CENTER
                    elif offset > 0:
                        new_steer = STEER_RIGHT
                    else:
                        new_steer = STEER_LEFT
                    if new_steer != self.last_steer:
                        self.do_steer(new_steer)
                        self.last_steer = new_steer
                    forward()
                else:
                    stop()
                    print("No blue")

        except KeyboardInterrupt:
            print("Stopped by user")
        except Exception as e:
            print("Error: {}".format(e))
        finally:
            self.cap.release()
            stop()
            print("Done")


try:
    for pin in [SERVO_PIN, ENA, IN1, IN2, IN3, IN4]:
        GPIO.setup(pin, GPIO.OUT)

    servo = GPIO.PWM(SERVO_PIN, 50)
    servo.start(7.2)
    print("Servo initialized...")
    time.sleep(1)

    print("Vision Testing...")

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