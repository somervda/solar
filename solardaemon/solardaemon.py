from renogy import Renogy
from solarlogger import SolarLogger
from solarrelay import SolarRelay
from solarcache import SolarCache
import time

_lastMainLoop = time.gmtime(time.time())
_loopCnt = 0
_batteryCapacity = 0
_solarPower = 0
_solarVolts = 0
_solarAmps = 0
_outputPower = 0

_lastBatteryCapacityRule = True
_lastWebcamRunAtNightRule = True


def main():
    initialize()
    while True:
        if _lastMainLoop.tm_hour != time.gmtime(time.time()).tm_hour:
            # Hour changed since last loop
            writeLog()
        updateState()
        time.sleep(60)


def initialize():
    print("Initialize")
    # Turn off extra devices when starting up
    sr = SolarRelay()
    sr.webcamOff()
    sr.rigOff()


def writeLog():
    global _lastMainLoop
    global _loopCnt
    global _batteryCapacity
    global _solarPower
    global _solarVolts
    global _solarAmps
    global _outputPower

    print("writeLog {}".format(_lastMainLoop.tm_hour))
    # Write log entry - use running totals averaged over the last hour
    sl = SolarLogger()
    if _loopCnt > 0:
        sl.writeData(round(_batteryCapacity / _loopCnt, 3), round(_solarPower /
                     _loopCnt, 3), round(_outputPower / _loopCnt, 3),
                     round(_solarAmps / _loopCnt, 3), round(_solarVolts / _loopCnt, 3))
    # Reset data for collection over next hour
    _loopCnt = 0
    _batteryCapacity = 0
    _solarPower = 0
    _outputPower = 0
    _solarAmps = 0
    _solarVolts = 0
    _lastMainLoop = time.gmtime(time.time())


def updateState():
    # Add renogy power stats to the running totals
    # Check power rules and modify power usage if needed
    global _loopCnt
    global _batteryCapacity
    global _solarPower
    global _solarVolts
    global _solarAmps
    global _outputPower
    global _lastBatteryCapacityRule
    global _lastWebcamRunAtNightRule

    r = Renogy()
    if _loopCnt > 0:
        print("updateState {} {} {} {} {} {} {} {}".format(time.strftime("%x %X", time.localtime(time.time())),
                                                           _loopCnt, round(r.batteryCapacity, 3), round(
                                                               r.solarPower, 3),
                                                           round(r.outputPower, 3), r.chargingModeDesc,  round(r.solarVolts, 3),  round(r.solarAmps, 3)))
    else:
        print("updateState ")
    # Perform management functions each minute
    _loopCnt += 1
    _batteryCapacity += r.batteryCapacity
    _solarPower += r.solarPower
    _solarVolts += r.solarVolts
    _solarAmps += r.solarAmps
    _outputPower += r.outputPower

    # **** webcam power rules  ***
    sc = SolarCache()
    # Set the basic rule of the webcam is normally on
    webcamRule = True
    info = ""
    if r.batteryCapacity < sc.powerSaveLevel:
        # Battery Power is too low, turn off webcam
        info += "batteryCapacity "
        webcamRule = False
    if not sc.webcamRunAtNight and r.chargingMode == 0:
        # Looks like its night time because no power being generated
        info += "webcamRunAtNight "
        webcamRule = False
    if sc.webcamTurnOffTime is not None:
        currentHour = time.localtime(time.time()).tm_hour
        # Turn off time only valid between 6PM and 6AM (Note - based on local times, not gmt time)
        if currentHour <= 6 or currentHour >= 18:
            # Some tricky conditions due to hour in scope may role over to next day for turning off in evening
            if (sc.webcamTurnOffTime >= 18 and (currentHour >= sc.webcamTurnOffTime or currentHour <= 6)) \
                    or (sc.webcamTurnOffTime <= 6 and (currentHour >= sc.webcamTurnOffTime)):
                info += "webcamTurnOffTime:" + str(currentHour) + " "
                webcamRule = False
    if sc.webcamExpiry is not None:
        if sc.webcamExpiry >= time.time():
            # Webcam expired still in future, overrides any other rules so leave on
            info += "webcamExpiryForcedOn "
            webcamRule = True
        else:
            # webcam expiry is expired so clear it out (webcam is no longer being forced on)
            # webcam state is based on the other rules
            sc.webcamExpiry = None
            sc.writeCache()

    # Check if we need to change the webcam state
    sr = SolarRelay()
    if sc.webcamOn != webcamRule:
        print("Rule Fired: " + info)
        print(sc.webcamOn)
        print(webcamRule)
        if webcamRule:
            sr.webcamOn()
        else:
            sr.webcamOff()

    # **** rig power rules  ***
    if sc.rigExpiry is not None:
        if sc.rigExpiry > time.time():
            # Rig expiry still in future, overrides any other rules so leave on
            if sc.rigOn == False:
                print("rig On rule")
                # This shouldn't occur
                sr.rigOn()
        else:
            # Rig is expired
            print("rig Off rule")
            if sc.rigOn:
                sr.rigOff()


# ************ Run solardaemon ************
main()
