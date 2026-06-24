import Jetson.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Pins - ENA and ENB are jumpered HIGH on the L298N
IN1 = 11  # Left forward
IN2 = 12  # Left backward
IN3 = 7   # Right forward
IN4 = 13  # Right backward

for pin in [IN1, IN2, IN3, IN4]:
    GPIO.setup(pin, GPIO.OUT)


def set_left(direction):
    """direction: 1=forward, -1=backward, 0=stop"""
    GPIO.output(IN1, direction > 0)
    GPIO.output(IN2, direction < 0)

def set_right(direction):
    """direction: 1=forward, -1=backward, 0=stop"""
    GPIO.output(IN3, direction > 0)
    GPIO.output(IN4, direction < 0)

def forward():
    set_left(1)
    set_right(1)

def backward():
    set_left(-1)
    set_right(-1)

def turn_left():
    """Pivot: left back, right forward"""
    set_left(-1)
    set_right(1)

def turn_right():
    """Pivot: left forward, right back"""
    set_left(1)
    set_right(-1)

def curve_left():
    """Left motor stopped, right forward"""
    set_left(0)
    set_right(1)

def curve_right():
    """Right motor stopped, left forward"""
    set_left(1)
    set_right(0)

def stop():
    set_left(0)
    set_right(0)


try:
    print("Forward")
    forward()
    time.sleep(1)

    print("Curve right")
    curve_right()
    time.sleep(1)

    print("Stop")
    stop()

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    try:
        stop()
    except:
        pass
    GPIO.cleanup()
    print("Done")