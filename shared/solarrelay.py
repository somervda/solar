# Manages the relays (webcam and ham rig) in my solar setup
# and update the solarcache to match the latest state.

from solarcache import SolarCache
import RPi.GPIO as GPIO
import time
import os
import psutil
import settings 
# from subprocess import PIPE, Popen


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

    def mumbleOn(self):
        # Start mumble client

        # Fire up mumble client as a background, headless process
        # Comment out required option
        # Option 1 - Show mumble gui so sound interface wizard can be run and stored for www-data user
        # os.system("export DISPLAY=PowerSpec-G703.home:0;nohup mumble mumble://rig:@rpi3.home 2> /dev/null &")

        # Option 2 -Hide GUI once config is setup.
        os.system("export DISPLAY=:99;nohup mumble mumble://rig:@" + settings.HOST + " 2> /dev/null &")

        # Check mumble is running
        mumbleIsRunning = False
        mumbleCnt = 0
        while mumbleCnt < 5 and not mumbleIsRunning:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info["name"] == "mumble":
                    mumbleIsRunning = True
            mumbleCnt+=1
            time.sleep(1)
        if  mumbleIsRunning:
            return ""
        else:
            return "mumble could not be started"

    def mumbleOff(self):
        # find and kill mumble client
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info["name"] == "mumble":
                proc.kill()
        os.system("export DISPLAY=" + settings.DEFAULT_XWINDOWS_SERVER)
        return ""

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
                # print(proc.info)
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
        # Fire up mumble
        mumbleResult = self.mumbleOn()
        time.sleep(1)
        # Success: Update solarcache.json info
        sc = SolarCache()
        sc.rigOn = True
        if updateExpiry:
            sc.rigExpiry = time.time() + (sc.rigExpiryMinutes * 60)
        else:
            sc.rigExpiry = None
        sc.writeCache()
        return ""

    def getMumbleState(self):
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info["name"] == "mumble":
                return "on"
        return "off"


    def rigOff(self):
        # find and kill the rigctld daemon
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info["name"] == "rigctld":
                proc.kill()
        # find and kill mumble client
        self.mumbleOff()
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

