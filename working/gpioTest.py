import RPi.GPIO as GPIO
import time

# Webcam uses gpio 20 and 21
# uSDR tranciever will use gpio 19
relay1_On = 21
relay1_Off = 20
relay2 = 19

GPIO.setmode(GPIO.BCM)  # Use the GPIO numbers (Not pins)
GPIO.setup(relay1_On, GPIO.OUT)
GPIO.setup(relay1_Off, GPIO.OUT)
GPIO.setup(relay2, GPIO.OUT)

print("Relay1 On")
GPIO.output(relay1_On, GPIO.HIGH)
time.sleep(0.05)
GPIO.output(relay1_On, GPIO.LOW)
time.sleep(2)
print("Relay1 Off")
GPIO.output(relay1_Off, GPIO.HIGH)
time.sleep(0.05)
GPIO.output(relay1_Off, GPIO.LOW)

time.sleep(1)
print("Relay2 On")
GPIO.output(relay2, GPIO.HIGH)
time.sleep(2)
print("Relay2 Off")
GPIO.output(relay2, GPIO.LOW)

GPIO.cleanup()
