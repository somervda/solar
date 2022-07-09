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
import fcntl
from os.path import exists
import time

class SolarCache:
    def __init__(self,solarcacheFN="../shared/solarcache.json"):
        self.solarcacheFN=solarcacheFN
        self.cache = {}
        if  exists(self.solarcacheFN):
            print("file found")
            with  open(self.solarcacheFN, "r") as cache_file:
                    fcntl.flock(cache_file, fcntl.LOCK_UN)
            self.loadCache()
        else:
            # Parameters added to cashe dictionary object  
            # powerSaveLevel: Available battery level in percent at witch the solar system will go into
            # full power saving mode (Usuall only power the RPI)
            self.cache["powerSaveLevel"]=50 
            # webcamRunAtNight: determines if webcam is turned on after dark (2Watts more power used at night for IR lighting)
            self.cache["webcamRunAtNight"]=False
            # webcamTurnOffTime: Time to turn the webcam off even if webcamRunAtNight is true None=No setting, 0-24=hourto turn off
            self.cache["webcamTurnOffTime"] = None
            # webcamExpiryMinutes: If the webcam is manually turned on, it is the time in minutes it expires/turns off (Sets webcamExpiry)
            self.cache["webcamExpiryMinutes"]=60
            # webcamExpiry: If webcam has been manually started this is the datetime until it is a candidate to be turned of 
            #    (Depending on other power management settings), value is a time value e.g. time.time() + (webCamExpiryMinutes * 60)
            self.cache["webcamExpiry"] = None
            # webcamOn: keep track of webcam on/off status
            self.cache["webcamOn"] = False
            # rigExpiryMinutes: If the ham rig is manually turned on, it is the time in minutes it will be turned off (Sets rigExpiry)
            self.cache["rigExpiryMinutes"]=60
            # rigExpiry: If ham rig has been manually started this is the datetime until it is turned off (After no activity), value is a time
            #    e.g. time.time() + (rigExpiryMinutes * 60)
            self.cache["rigExpiry"] = None
            # rigOn: keep track of ham rig on/off status
            self.cache["rigOn"] = False

    def writeCache(self):
        for looper in range(5) : # try and get lock on file 5 times
            try:#try/except in case the file is still locked by another process
                with  open(self.solarcacheFN, "w") as cache_file: #open the file for writting
                    fcntl.flock(cache_file, fcntl.LOCK_EX | fcntl.LOCK_NB)#lock the file
                    cache_file.write(json.dumps(self.cache))
                    fcntl.flock(cache_file, fcntl.LOCK_UN)#and now unlock it so other processed can edit it!
                    break
            except IOError as e:
                print(self.solarcacheFN + " locked while writing")
                time.sleep(0.5) #wait before retrying

    def loadCache(self):
        cacheS="{}"
        for looper in range(5) : # try and get lock on file 5 times
            try:#try/except in case the file is still locked by another process
                with  open(self.solarcacheFN, "r") as cache_file: #open the file for reading
                    fcntl.flock(cache_file, fcntl.LOCK_EX | fcntl.LOCK_NB)#lock the file
                    cacheS=cache_file.read()
                    fcntl.flock(cache_file, fcntl.LOCK_UN)#and now unlock it so other processed can edit it!
                    break
            except IOError as e:
                print(self.solarcacheFN + " locked while loading")
                time.sleep(0.5) #wait before retrying
        # Only load supported properties
        cache=json.loads(cacheS)
        self.cache = {}
        if "powerSaveLevel" in cache :
            self.cache["powerSaveLevel"]=cache["powerSaveLevel"]
        else:
            self.cache["powerSaveLevel"]=50 

        if "webcamRunAtNight" in cache :
            self.cache["webcamRunAtNight"]=cache["webcamRunAtNight"]
        else:
            self.cache["webcamRunAtNight"]=False 

        if "webcamTurnOffTime" in cache :
            self.cache["webcamTurnOffTime"]=cache["webcamTurnOffTime"]
        else:
            self.cache["webcamTurnOffTime"]=None

        if "webcamExpiryMinutes" in cache :
            self.cache["webcamExpiryMinutes"]=cache["webcamExpiryMinutes"]
        else:
            self.cache["webcamExpiryMinutes"]=60 
        
        if "webcamExpiry" in cache :
            self.cache["webcamExpiry"]=cache["webcamExpiry"]
        else:
            self.cache["webcamExpiry"]=None

        if "webcamOn" in cache :
            self.cache["webcamOn"]=cache["webcamOn"]
        else:
            self.cache["webcamOn"]=False 

        if "rigExpiryMinutes" in cache :
            self.cache["rigExpiryMinutes"]=cache["rigExpiryMinutes"]
        else:
            self.cache["rigExpiryMinutes"]=60 
        
        if "rigExpiry" in cache :
            self.cache["rigExpiry"]=cache["rigExpiry"]
        else:
            self.cache["rigExpiry"]=None

        if "rigOn" in cache :
            self.cache["rigOn"]=cache["rigOn"]
        else:
            self.cache["rigOn"]=False 

