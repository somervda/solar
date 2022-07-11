# Manages the relays (webcam and ham rig) in my solar setup
# and update the solarcache to match the latest state.

from solarcache import SolarCache
import RPi.GPIO as GPIO
import time


class SolarRelay:
    def __init__(self):
        # Webcam uses gpio 20 and 21
        # uSDR transciever will use gpio 19
        self.webcamOnGPIO = 21
        self.webcamOffGPIO = 20
        self.rigGPIO = 19
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)  # Use the GPIO numbers (Not pins)
        GPIO.setup(self.webcamOnGPIO, GPIO.OUT)
        GPIO.setup(self.webcamOffGPIO, GPIO.OUT)
        GPIO.setup(self.rigGPIO, GPIO.OUT)

    def webcamOn(self, updateExpiry=False):
        # updateExpiry only used whencalled as a manual power on from web service
        GPIO.output(self.webcamOnGPIO, GPIO.HIGH)
        time.sleep(0.05)
        GPIO.output(self.webcamOnGPIO, GPIO.LOW)
        time.sleep(0.05)
        # Update solarcache.json info
        sc = SolarCache()
        sc.webcamOn = True
        if updateExpiry:
            sc.webcamExpiry = time.time() + (sc.webcamExpiryMinutes * 60)
        else:
            sc.webcamExpiry = None
        sc.writeCache()
        pass

    def webcamOff(self):
        GPIO.output(self.webcamOffGPIO, GPIO.HIGH)
        time.sleep(0.05)
        GPIO.output(self.webcamOffGPIO, GPIO.LOW)
        time.sleep(0.05)
        # Update solarcache.json info
        sc = SolarCache()
        sc.webcamOn = False
        sc.webcamExpiry = None
        sc.writeCache()

    def rigOn(self, updateExpiry=False):
        # updateExpiry only used when called as a manual power on from web service
        GPIO.output(self.rigGPIO, GPIO.HIGH)
        # Update solarcache.json info
        sc = SolarCache()
        sc.rigOn = True
        if updateExpiry:
            sc.rigExpiry = time.time() + (sc.rigExpiryMinutes * 60)
        else:
            sc.rigExpiry = None
        sc.writeCache()

    def rigOff(self):
        GPIO.output(self.rigGPIO, GPIO.LOW)
        # Update solarcache.json info
        sc = SolarCache()
        sc.rigOn = False
        sc.rigExpiry = None
        sc.writeCache()
