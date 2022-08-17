# Manages the relays (webcam and ham rig) in my solar setup
# and update the solarcache to match the latest state.

from solarcache import SolarCache
import RPi.GPIO as GPIO
import time
import os
import psutil


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
        # Turn on the rig relay
        GPIO.output(self.rigGPIO, GPIO.HIGH)
        # turn on the USB hardware on the RPI
        # Improves on : os.system("echo '1-1' | tee /sys/bus/usb/drivers/usb/bind")
        # Note: May get an exception if the usb subsystem is already bound
        try:
            with open("/sys/bus/usb/drivers/usb/bind", "w") as usb_bind:
                usb_bind.write("1-1")
        except:
            print("rigOn usb bind skipped")
        # Wait 1 second for the rig and usb to power on , then fire up rigctld
        time.sleep(1)
        if not os.path.exists("/dev/ttyUSB0"):
            # Failed to find /dev/ttyUSB0 serial port
            # turn off the USB hardware on the RPI
            # Note: May get an exception if the usb subsystem is already unbound
            try:
                with open("/sys/bus/usb/drivers/usb/unbind", "w") as usb_unbind:
                    usb_unbind.write("1-1")
            except:
                print("rigOn usb unbind skipped 01")
            # Turn off the rig relay
            GPIO.output(self.rigGPIO, GPIO.LOW)
            return "/dev/ttyUSB0 not found"

        #  Start rigctld
        os.system(
            "nohup /home/pi/local/bin/rigctld -m 2028 -s 38400 -r /dev/ttyUSB0 &")
        # Wait for 1 second and check that rigctl started
        time.sleep(1)
        rigctldIsRunning = False
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info["name"] == "rigctld":
                rigctldIsRunning = True
                print(proc.info)
        if not rigctldIsRunning:
            # Failed to run rigctld
            # turn off the USB hardware on the RPI
            # Note: May get an exception if the usb subsystem is already unbound
            try:
                with open("/sys/bus/usb/drivers/usb/unbind", "w") as usb_unbind:
                    usb_unbind.write("1-1")
            except:
                print("rigOn usb unbind skipped 02")
            # Turn off the rig relay
            GPIO.output(self.rigGPIO, GPIO.LOW)
            return "rigctld could not be started"

        # Success: Update solarcache.json info
        sc = SolarCache()
        sc.rigOn = True
        if updateExpiry:
            sc.rigExpiry = time.time() + (sc.rigExpiryMinutes * 60)
        else:
            sc.rigExpiry = None
        sc.writeCache()
        return ""

    def rigOff(self):
        # find and kill the rigctld daemon
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info["name"] == "rigctld":
                proc.kill()
        # turn off the USB hardware on the RPI
        # Improves on: os.system("echo '1-1' | tee /sys/bus/usb/drivers/usb/unbind")
        # Note: May get an exception if the usb subsystem is already unbound
        try:
            with open("/sys/bus/usb/drivers/usb/unbind", "w") as usb_unbind:
                usb_unbind.write("1-1")
        except:
            print("rigOff usb unbind skipped")
        # Turn off the rig relay
        GPIO.output(self.rigGPIO, GPIO.LOW)
        # Update solarcache.json info
        sc = SolarCache()
        sc.rigOn = False
        sc.rigExpiry = None
        sc.writeCache()
