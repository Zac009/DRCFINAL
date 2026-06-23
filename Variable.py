import Jetson.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Pins
ENA = 32
ENA       = 32
IN1       = 11
IN2       = 12
IN3       = 7
IN4       = 13
try:
    # Setup pins
    for pin in [ENA, IN1, IN2, IN3, IN4]:
        GPIO.setup(pin, GPIO.OUT)

    # PWM on ENA at 1 kHz
    motor_pwm = GPIO.PWM(ENA, 1000)
    motor_pwm.start(0)

    def forward(speed):
        # speed = 0-100 (%)
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)

        motor_pwm.ChangeDutyCycle(speed)

    def reverse(speed):
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH)

        motor_pwm.ChangeDutyCycle(speed)

    def stop():
        motor_pwm.ChangeDutyCycle(0)
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.LOW)

    # Test speeds
    speeds = [50, 100]

    for speed in speeds:
        print(f"Forward at {speed}%")
        forward(speed)
        time.sleep(1)

        print("Stop")
        stop()
        time.sleep(1)
        
except KeyboardInterrupt:
    pass

finally:
    stop()
    motor_pwm.stop()
    GPIO.cleanup()
    print("Done")