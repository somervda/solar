# The solarcache class manages the interface to the solarcache.json file
# The solarcache.json file contains the run time parameters for the solar demon
# i.e. What to do when the battery drops below a particular level, as
# well as timing parameters for how long the webcam and radio should be powered
# before being turned off.
# It also contains more transitive parameters like how long relays have been turned on.
# The class exposes all this data in a single name space as well as managing
# locking and reading/writting of the solarcache.json file. This class
# will be used by the solardemon and the solarwww web service processes.

import json
from os.path import exists
import time


class SolarCache:
    def __init__(self, solarcacheFN="/home/pi/solar/shared/solarcache.json"):
        self.solarcacheFN = solarcacheFN
        self.cache = {}
        if exists(self.solarcacheFN):
            self.loadCache()
        else:
            # Parameters added to cashe dictionary object
            # powerSaveLevel: Available battery level in percent at witch the solar system will go into
            # full power saving mode (Usuall only power the RPI)
            self.cache["powerSaveLevel"] = 50
            # webcamRunAtNight: determines if webcam is turned on after dark (2Watts more power used at night for IR lighting)
            self.cache["webcamRunAtNight"] = False
            # webcamTurnOffTime: Time to turn the webcam off even if webcamRunAtNight is true None=No setting, 0-24=hourto turn off
            self.cache["webcamTurnOffTime"] = None
            # webcamExpiryMinutes: If the webcam is manually turned on, it is the time in minutes it expires/turns off (Sets webcamExpiry)
            self.cache["webcamExpiryMinutes"] = 60
            # webcamExpiry: If webcam has been manually started this is the datetime until it is a candidate to be turned of
            #    (Depending on other power management settings), value is a time value e.g. time.time() + (webCamExpiryMinutes * 60)
            self.cache["webcamExpiry"] = None
            # webcamOn: keep track of webcam on/off status
            self.cache["webcamOn"] = False
            # rigExpiryMinutes: If the ham rig is manually turned on, it is the time in minutes it will be turned off (Sets rigExpiry)
            self.cache["rigExpiryMinutes"] = 60
            # rigExpiry: If ham rig has been manually started this is the datetime until it is turned off (After no activity), value is a time
            #    e.g. time.time() + (rigExpiryMinutes * 60)
            self.cache["rigExpiry"] = None
            # rigOn: keep track of ham rig on/off status
            self.cache["rigOn"] = False
            self.writeCache()

    # Getters and setters
    @property
    def powerSaveLevel(self):
        return self.cache["powerSaveLevel"]

    @powerSaveLevel.setter
    def powerSaveLevel(self, powerSaveLevel):
        self.cache["powerSaveLevel"] = powerSaveLevel

    @property
    def webcamRunAtNight(self):
        return self.cache["webcamRunAtNight"]

    @webcamRunAtNight.setter
    def webcamRunAtNight(self, webcamRunAtNight):
        self.cache["webcamRunAtNight"] = webcamRunAtNight

    @property
    def webcamTurnOffTime(self):
        return self.cache["webcamTurnOffTime"]

    @webcamTurnOffTime.setter
    def webcamTurnOffTime(self, webcamTurnOffTime):
        self.cache["webcamTurnOffTime"] = webcamTurnOffTime

    @property
    def webcamExpiryMinutes(self):
        return self.cache["webcamExpiryMinutes"]

    @webcamExpiryMinutes.setter
    def webcamExpiryMinutes(self, webcamExpiryMinutes):
        self.cache["webcamExpiryMinutes"] = webcamExpiryMinutes

    @property
    def webcamExpiry(self):
        return self.cache["webcamExpiry"]

    @webcamExpiry.setter
    def webcamExpiry(self, webcamExpiry):
        self.cache["webcamExpiry"] = webcamExpiry

    @property
    def webcamOn(self):
        return self.cache["webcamOn"]

    @webcamOn.setter
    def webcamOn(self, webcamOn):
        self.cache["webcamOn"] = webcamOn

    @property
    def rigExpiryMinutes(self):
        return self.cache["rigExpiryMinutes"]

    @rigExpiryMinutes.setter
    def rigExpiryMinutes(self, rigExpiryMinutes):
        self.cache["rigExpiryMinutes"] = rigExpiryMinutes

    @property
    def rigExpiry(self):
        return self.cache["rigExpiry"]

    @rigExpiry.setter
    def rigExpiry(self, rigExpiry):
        self.cache["rigExpiry"] = rigExpiry

    @property
    def rigOn(self):
        return self.cache["rigOn"]

    @rigOn.setter
    def rigOn(self, rigOn):
        self.cache["rigOn"] = rigOn

    def writeCache(self):
        with open(self.solarcacheFN, "w") as cache_file:
            cache_file.write(json.dumps(self.cache))

    def loadCache(self):
        with open(self.solarcacheFN, "r") as cache_file:  # open the file for reading
            cache = json.loads(cache_file.read())
        # Only load supported properties
        self.cache = {}
        if "powerSaveLevel" in cache:
            self.cache["powerSaveLevel"] = cache["powerSaveLevel"]
        else:
            self.cache["powerSaveLevel"] = 50

        if "webcamRunAtNight" in cache:
            self.cache["webcamRunAtNight"] = cache["webcamRunAtNight"]
        else:
            self.cache["webcamRunAtNight"] = False

        if "webcamTurnOffTime" in cache:
            self.cache["webcamTurnOffTime"] = cache["webcamTurnOffTime"]
        else:
            self.cache["webcamTurnOffTime"] = None

        if "webcamExpiryMinutes" in cache:
            self.cache["webcamExpiryMinutes"] = cache["webcamExpiryMinutes"]
        else:
            self.cache["webcamExpiryMinutes"] = 60

        if "webcamExpiry" in cache:
            self.cache["webcamExpiry"] = cache["webcamExpiry"]
        else:
            self.cache["webcamExpiry"] = None

        if "webcamOn" in cache:
            self.cache["webcamOn"] = cache["webcamOn"]
        else:
            self.cache["webcamOn"] = False

        if "rigExpiryMinutes" in cache:
            self.cache["rigExpiryMinutes"] = cache["rigExpiryMinutes"]
        else:
            self.cache["rigExpiryMinutes"] = 60

        if "rigExpiry" in cache:
            self.cache["rigExpiry"] = cache["rigExpiry"]
        else:
            self.cache["rigExpiry"] = None

        if "rigOn" in cache:
            self.cache["rigOn"] = cache["rigOn"]
        else:
            self.cache["rigOn"] = False
