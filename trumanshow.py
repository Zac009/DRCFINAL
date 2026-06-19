import Jetson.GPIO as GPIO
import time
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

try:
    for pin in [SERVO_PIN, ENA, IN1, IN2, IN3, IN4]:
        GPIO.setup(pin, GPIO.OUT)

    servo = GPIO.PWM(SERVO_PIN, 50)
    servo.start(7.5)
    time.sleep(1)

    STEER_LEFT       = 8
    STEER_CENTER     = 7.5
    STEER_RIGHT      = 7
    MIN_CONTOUR_AREA = 500

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
        steer_center()


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
            steer_center()
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
                    MIN_CONTOUR_AREA = 0
                    if contours_blue:
                        largest_blue = max(contours_blue, key=cv2.contourArea)
                        if cv2.contourArea(largest_blue) > MIN_CONTOUR_AREA:
                            M = cv2.moments(largest_blue)
                            if M["m00"] != 0:
                                blue_x = int(M["m10"] / M["m00"])

                    if blue_x is not None:
                        frame_center = self.width // 2
                        offset       = blue_x - frame_center
                        print(f"Blue at x={blue_x} offset={offset}")
                        if abs(offset) < 20:
                            self.do_steer(STEER_CENTER)
                        elif offset > 0:
                            self.do_steer(STEER_RIGHT)
                        else:
                            self.do_steer(STEER_LEFT)
                        forward()
                        print("Forward")
                    else:
                        print("No blue")

            except KeyboardInterrupt:
                print("Stopped by user")
            except Exception as e:
                print(f"Error: {e}")
            finally:
                    self.cap.release()
                    print("Done")



    Ben = Vision()
    Ben.main()
finally:
    try:
        stop()
    except:
        pass
    try:
        servo.stop()
    except:
        pass
    GPIO.cleanup()    # only once, at the very end
    print("Done")