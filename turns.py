import Jetson.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

SERVO_PIN = 33

GPIO.setup(SERVO_PIN, GPIO.OUT)
servo = GPIO.PWM(SERVO_PIN, 50)

servo.start(7.5)  # center
time.sleep(1)

try:
    print("Left")
    servo.ChangeDutyCycle(8.0)
    time.sleep(1)

    """print("Center")
    servo.ChangeDutyCycle(7.5)
    time.sleep(1)

    print("Right")
    servo.ChangeDutyCycle(7.0)
    time.sleep(1)

    print("Center")
    servo.ChangeDutyCycle(7.5)
    time.sleep(1)"""

finally:
    servo.stop()
    GPIO.cleanup()