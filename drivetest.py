import Jetson.GPIO as GPIO
import time

# GPIO pin setup
STEER_PIN = 33
DRIVE_PIN = 32

# Servo pulse values
STEER_LEFT   = 1000
STEER_CENTER = 1500
STEER_RIGHT  = 2000

DRIVE_STOP     = 1500
DRIVE_FORWARD  = 1680
DRIVE_BACKWARD = 1400

PWM_FREQ = 50

def pulse_to_duty(pulse_us):
    period_us = 1_000_000 / PWM_FREQ
    return (pulse_us / period_us) * 100

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(STEER_PIN, GPIO.OUT)
    GPIO.setup(DRIVE_PIN, GPIO.OUT)
    steer_pwm = GPIO.PWM(STEER_PIN, PWM_FREQ)
    drive_pwm = GPIO.PWM(DRIVE_PIN, PWM_FREQ)
    steer_pwm.start(pulse_to_duty(STEER_CENTER))
    drive_pwm.start(pulse_to_duty(DRIVE_STOP))
    return steer_pwm, drive_pwm

def steer(pwm, pulse):
    pwm.ChangeDutyCycle(pulse_to_duty(pulse))

def drive(pwm, pulse):
    pwm.ChangeDutyCycle(pulse_to_duty(pulse))

def stop(drive_pwm, steer_pwm):
    drive(drive_pwm, DRIVE_STOP)
    steer(steer_pwm, STEER_CENTER)

# --- Main ---
steer_pwm, drive_pwm = setup()

try:
    print("Forward")
    steer(steer_pwm, STEER_CENTER)
    drive(drive_pwm, DRIVE_FORWARD)
    time.sleep(2)
    stop(drive_pwm, steer_pwm)
    time.sleep(0.5)

    print("Backward")
    steer(steer_pwm, STEER_CENTER)
    drive(drive_pwm, DRIVE_BACKWARD)
    time.sleep(2)
    stop(drive_pwm, steer_pwm)
    time.sleep(0.5)

    print("Left")
    steer(steer_pwm, STEER_LEFT)
    drive(drive_pwm, DRIVE_FORWARD)
    time.sleep(2)
    stop(drive_pwm, steer_pwm)
    time.sleep(0.5)

    print("Right")
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