import Jetson.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Pins
LEFT_EN  = 32
RIGHT_EN = 33
IN1 = 11  # Left forward
IN2 = 12  # Left backward
IN3 = 7   # Right forward
IN4 = 13  # Right backward

for pin in [LEFT_EN, RIGHT_EN, IN1, IN2, IN3, IN4]:
    GPIO.setup(pin, GPIO.OUT)

# PWM for independent speed control
left_pwm  = GPIO.PWM(LEFT_EN, 100)
right_pwm = GPIO.PWM(RIGHT_EN, 100)
left_pwm.start(0)
right_pwm.start(0)


def set_left(speed):
    """speed: -100 to 100"""
    if speed > 0:
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
    elif speed < 0:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
    else:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)
    left_pwm.ChangeDutyCycle(abs(speed))

def set_right(speed):
    """speed: -100 to 100"""
    if speed > 0:
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)
    elif speed < 0:
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH)
    else:
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.LOW)
    right_pwm.ChangeDutyCycle(abs(speed))

def forward(speed=80):
    set_left(speed)
    set_right(speed)

def backward(speed=80):
    set_left(-speed)
    set_right(-speed)

def curve_left(speed=80, factor=0.4):
    """Gentle left curve: slow left, full right"""
    set_left(int(speed * factor))
    set_right(speed)

def curve_right(speed=100, factor=0.4):
    """Gentle right curve: full left, slow right"""
    set_left(speed)
    set_right(int(speed * factor))

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
        left_pwm.stop()
        right_pwm.stop()
    except:
        pass
    GPIO.cleanup()
    print("Done")