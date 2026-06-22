import Jetson.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)
pwm = GPIO.PWM(12, 50)
pwm.start(7.5)  # ~1500us neutral
time.sleep(5)
pwm.stop()
GPIO.cleanup()