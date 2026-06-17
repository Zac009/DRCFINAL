import Jetson.GPIO as GPIO
import time
import sys
import tty
import termios

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Pins
SERVO_PIN = 33
ENA       = 32
IN1       = 12
IN2       = 11
IN3       = 7
IN4       = 13

for pin in [SERVO_PIN, ENA, IN1, IN2, IN3, IN4]:
    GPIO.setup(pin, GPIO.OUT)

servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(7.5)
time.sleep(1)

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
    servo.ChangeDutyCycle(5.0)

def steer_right():
    servo.ChangeDutyCycle(10.0)

def steer_center():
    servo.ChangeDutyCycle(7.5)

def stop():
    GPIO.output(ENA, GPIO.LOW)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    steer_center()

def get_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
        # handle arrow keys (escape sequences)
        if key == '\x1b':
            key += sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return key

print("Controls: W=forward  S=backward  A=left  D=right  SPACE=stop  Q=quit")
print("Arrow keys also work")

try:
    while True:
        key = get_key().lower()

        if key in ('w', '\x1b[A'):
            print("Forward")
            forward()
        elif key in ('s', '\x1b[B'):
            print("Backward")
            backward()
        elif key in ('a', '\x1b[D'):
            print("Left")
            steer_left()
        elif key in ('d', '\x1b[C'):
            print("Right")
            steer_right()
        elif key == ' ':
            print("Stop")
            stop()
        elif key == 'q':
            print("Quit")
            break

except KeyboardInterrupt:
    print("Stopped")

finally:
    try:
        stop()
        servo.stop()
    except:
        pass
    GPIO.cleanup()
    print("Done")