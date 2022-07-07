import RPi.GPIO as GPIO
import time

relay1_On = 21


GPIO.setmode(GPIO.BCM)  # Use the GPIO numbers (Not pins)
GPIO.setup(relay1_On, GPIO.OUT)


print("Webcam On")
GPIO.output(relay1_On, GPIO.HIGH)
time.sleep(0.05)
GPIO.output(relay1_On, GPIO.LOW)
