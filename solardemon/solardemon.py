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


def main():
    initialize()
    while True:
        if _lastMainLoop.tm_hour != time.gmtime(time.time()).tm_hour:
            # Hour changed since last loop
            writeLog()
        else:
            processStatus()
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
    print("writeLog {}".format(_lastMainLoop.tm_hour))
    # Write log entry - us values from renogy averaged over the last hour
    sl = SolarLogger()
    if _loopCnt > 0:
        sl.writeData(_batteryCapacity / _loopCnt, _solarPower /
                     _loopCnt, _outputPower / _loopCnt)
    # Reset data for collection over next hour
    _loopCnt = 0
    _batteryCapacity = 0
    _solarPower = 0
    _outputPower = 0
    _lastMainLoop = time.gmtime(time.time())


def processStatus():
    global _loopCnt
    global _batteryCapacity
    global _solarPower
    global _outputPower
    if _loopCnt > 0:
        print("processStatus {} {} {} {}".format(
            _loopCnt, _batteryCapacity / _loopCnt, _solarPower / _loopCnt, _outputPower / _loopCnt))
    else:
        print("processStatus")
    # Perform management functions each minute
    _loopCnt += 1
    r = Renogy()
    _batteryCapacity += r.batteryCapacity
    _solarPower += r.solarPower
    _outputPower += r.outputPower


# ************ Run solardemon ************
main()
