import Jetson.GPIO as GPIO
import time
import sys
import tty
import termios
import subprocess


"""subprocess.run(["sudo", "sh", "-c", "echo 0 > /sys/class/pwm/pwmchip0/export"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
subprocess.run(["sudo", "sh", "-c", "echo 20000000 > /sys/class/pwm/pwmchip0/pwm0/period"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)"""

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Pins
SERVO_PIN = 33
ENA       = 32
IN1       = 11
IN2       = 12
IN3       = 7
IN4       = 13

for pin in [SERVO_PIN, ENA, IN1, IN2, IN3, IN4]:
    GPIO.setup(pin, GPIO.OUT)

servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(7.5)
time.sleep(1.5)


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
    servo.ChangeDutyCycle(8.0)

def steer_right():
    servo.ChangeDutyCycle(7.0)

def steer_center():
    servo.ChangeDutyCycle(7.5)

def steer(pulse):
    servo.ChangeDutyCycle(pulse)

def stop():
    GPIO.output(ENA, GPIO.LOW)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    steer_center()

try:
    print("Forward")
    steer_center()
    forward()
    time.sleep(2)

    print("Right")
    steer_right()
    time.sleep(2)

    print("Stop")
    stop()

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    try:
        stop()
        servo.stop()
    except:
        pass
    GPIO.cleanup()
    print("Done")
