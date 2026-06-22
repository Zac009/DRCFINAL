import Jetson.GPIO as GPIO
import time

# GPIO pin setup
STEER_PIN     = 32  # PWM - Steering servo
DRIVE_PIN     = 33  # PWM - Drive speed

MOTOR_RIGHT_A = 13  # Right motor direction pin 1
MOTOR_RIGHT_B = 11  # Right motor direction pin 2
MOTOR_LEFT_A  = 7   # Left motor direction pin 1
MOTOR_LEFT_B  = 12   # Left motor direction pin 2

# Servo pulse values
STEER_LEFT     = 1000
STEER_CENTER   = 1500
STEER_RIGHT    = 2000

DRIVE_STOP     = 1500
DRIVE_FORWARD  = 1680
DRIVE_BACKWARD = 1400

PWM_FREQ = 50

def pulse_to_duty(pulse_us):
    period_us = 1_000_000 / PWM_FREQ
    return (pulse_us / period_us) * 100

def setup():
    GPIO.setmode(GPIO.BOARD)

    # PWM pins
    GPIO.setup(STEER_PIN, GPIO.OUT)
    GPIO.setup(DRIVE_PIN, GPIO.OUT)

    # Motor direction pins
    GPIO.setup(MOTOR_RIGHT_A, GPIO.OUT)
    GPIO.setup(MOTOR_RIGHT_B, GPIO.OUT)
    GPIO.setup(MOTOR_LEFT_A,  GPIO.OUT)
    GPIO.setup(MOTOR_LEFT_B,  GPIO.OUT)

    steer_pwm = GPIO.PWM(STEER_PIN, PWM_FREQ)
    drive_pwm = GPIO.PWM(DRIVE_PIN, PWM_FREQ)
    steer_pwm.start(pulse_to_duty(STEER_CENTER))
    drive_pwm.start(pulse_to_duty(DRIVE_STOP))

    motor_stop()

    return steer_pwm, drive_pwm

def steer(pwm, pulse):
    pwm.ChangeDutyCycle(pulse_to_duty(pulse))

def drive(pwm, pulse):
    pwm.ChangeDutyCycle(pulse_to_duty(pulse))

def motor_forward():
    GPIO.output(MOTOR_RIGHT_A, GPIO.HIGH)
    GPIO.output(MOTOR_RIGHT_B, GPIO.LOW)
    GPIO.output(MOTOR_LEFT_A,  GPIO.HIGH)
    GPIO.output(MOTOR_LEFT_B,  GPIO.LOW)

def motor_backward():
    GPIO.output(MOTOR_RIGHT_A, GPIO.LOW)
    GPIO.output(MOTOR_RIGHT_B, GPIO.HIGH)
    GPIO.output(MOTOR_LEFT_A,  GPIO.LOW)
    GPIO.output(MOTOR_LEFT_B,  GPIO.HIGH)

def motor_stop():
    GPIO.output(MOTOR_RIGHT_A, GPIO.LOW)
    GPIO.output(MOTOR_RIGHT_B, GPIO.LOW)
    GPIO.output(MOTOR_LEFT_A,  GPIO.LOW)
    GPIO.output(MOTOR_LEFT_B,  GPIO.LOW)

def stop(drive_pwm, steer_pwm):
    drive(drive_pwm, DRIVE_STOP)
    steer(steer_pwm, STEER_CENTER)
    motor_stop()

# --- Main ---
steer_pwm, drive_pwm = setup()

try:
    print("Forward")
    motor_forward()
    steer(steer_pwm, STEER_CENTER)
    drive(drive_pwm, DRIVE_FORWARD)
    time.sleep(2)
    stop(drive_pwm, steer_pwm)
    time.sleep(0.5)

    """print("Backward")
    motor_backward()
    steer(steer_pwm, STEER_CENTER)
    drive(drive_pwm, DRIVE_BACKWARD)
    time.sleep(2)
    stop(drive_pwm, steer_pwm)
    time.sleep(0.5)"""

    """print("Left")
    motor_forward()
    steer(steer_pwm, STEER_LEFT)
    drive(drive_pwm, DRIVE_FORWARD)
    time.sleep(2)
    stop(drive_pwm, steer_pwm)
    time.sleep(0.5)"""

    print("Right")
    motor_forward()
    steer(steer_pwm, STEER_RIGHT)
    drive(drive_pwm, DRIVE_FORWARD)
    time.sleep(2)
    stop(drive_pwm, steer_pwm)

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    stop(drive_pwm, steer_pwm)
    steer_pwm.stop()
    drive_pwm.stop()
    GPIO.cleanup()
    print("GPIO cleaned up")