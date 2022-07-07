import RPi.GPIO as GPIO
import time

relay1_Off = 20


GPIO.setmode(GPIO.BCM)  # Use the GPIO numbers (Not pins)
GPIO.setup(relay1_Off, GPIO.OUT)

print("Webcam Off")
GPIO.output(relay1_Off, GPIO.HIGH)
time.sleep(0.05)
GPIO.output(relay1_Off, GPIO.LOW)
