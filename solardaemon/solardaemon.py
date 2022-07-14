from renogy import Renogy
from solarlogger import SolarLogger
from solarrelay import SolarRelay
from solarcache import SolarCache
import time

_lastMainLoop = time.gmtime(time.time())
_loopCnt = 0
_batteryCapacity = 0
_solarPower = 0
_outputPower = 0

_lastBatteryCapacityRule = True
_lastWebcamRunAtNightRule = True

_modeNC = 0
_modeBulk = 0
_modeBoost = 0
_modeFloat = 0
_modeEql = 0
_modeOther = 0


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
    global _outputPower

    global _modeNC
    global _modeBulk
    global _modeBoost
    global _modeFloat
    global _modeEql
    global _modeOther
    print("writeLog {}".format(_lastMainLoop.tm_hour))
    # Write log entry - use running totals averaged over the last hour
    sl = SolarLogger()
    if _loopCnt > 0:
        sl.writeData(round(_batteryCapacity / _loopCnt, 3), round(_solarPower /
                     _loopCnt, 3), round(_outputPower / _loopCnt, 3), round(_modeNC * 100/_loopCnt, 0),  round(_modeBulk * 100/_loopCnt, 0), round(_modeBoost * 100/_loopCnt, 0), round(_modeFloat * 100/_loopCnt, 0), round(_modeEql * 100/_loopCnt, 0), round(_modeOther * 100/_loopCnt, 0))
    # Reset data for collection over next hour
    _loopCnt = 0
    _batteryCapacity = 0
    _solarPower = 0
    _outputPower = 0
    _modeNC = 0
    _modeBulk = 0
    _modeBoost = 0
    _modeFloat = 0
    _modeEql = 0
    _modeOther = 0
    _lastMainLoop = time.gmtime(time.time())


def updateState():
    # Add renogy power stats to the running totals
    # Check power rules and modify power usage if needed
    global _loopCnt
    global _batteryCapacity
    global _solarPower
    global _outputPower
    global _lastBatteryCapacityRule
    global _lastWebcamRunAtNightRule

    global _modeNC
    global _modeBulk
    global _modeBoost
    global _modeFloat
    global _modeEql
    global _modeOther
    r = Renogy()
    if _loopCnt > 0:
        print("updateState {} {} {} {} {} {}".format(time.strftime("%x %X", time.localtime(time.time())),
                                                     _loopCnt, round(r.batteryCapacity, 3), round(r.solarPower, 3), round(r.outputPower, 3), r.chargingModeDesc))
    else:
        print("updateState ")
    # Perform management functions each minute
    _loopCnt += 1
    _batteryCapacity += r.batteryCapacity
    _solarPower += r.solarPower
    _outputPower += r.outputPower
    #  Add to the charging mode trackers

    if r.chargingMode == 0:  # No charging
        _modeNC += 1
    elif r.chargingMode == 1:  # Activated
        _modeOther += 1
    elif r.chargingMode == 2:  # MPPT
        _modeBulk += 1
    elif r.chargingMode == 3:  # Equalizing
        _modeEql += 1
    elif r.chargingMode == 4:  # Boost
        _modeBoost += 1
    elif r.chargingMode == 5:  # Float
        _modeFloat += 1
    elif r.chargingMode == 6:  # Overpowered (Current limited)
        _modeOther += 1
    else:
        _modeOther += 1

    # **** webcam power rules  ***
    sc = SolarCache()
    # Set the basic rule of the webcam is normally on
    webcamRule = True
    info = ""
    # Use a sample size of more than 5 for renogy data (cut down false positives on status)
    if _loopCnt > 5:
        if _batteryCapacity/_loopCnt < sc.powerSaveLevel:
            # Battery Power is too low, turn off webcam
            info += "batteryCapacity "
            webcamRule = False
        if not sc.webcamRunAtNight and _solarPower/_loopCnt < 0.01:
            # Looks like its night time because no power being generated
            info += "webcamRunAtNight "
            webcamRule = False
    else:
        # No determination can be made for the history based rules so apply last values
        if _lastWebcamRunAtNightRule == False or _lastBatteryCapacityRule == False:
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
