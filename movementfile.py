import Jetson.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

SERVO_PIN = 33
ENA       = 32
IN1       = 12
IN2       = 11
IN3       = 7
IN4       = 13

for pin in [SERVO_PIN, ENA, IN1, IN2, IN3, IN4]:
    GPIO.setup(pin, GPIO.OUT)

servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(7.5)  # full left