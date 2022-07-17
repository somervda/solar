from flask import Flask
from renogy import Renogy
from solarlogger import SolarLogger
import time


app = Flask(__name__)


@app.route("/renogystatus")
def renogystatus():
    r = Renogy()
    data = {}
    data["batteryCapacity"] = r.batteryCapacity
    data["batteryVoltage"] = r.batteryVoltage
    data["solarPower"] = r.solarPower
    data["solarVolts"] = r.solarVolts
    data["solarAmps"] = r.solarAmps
    data["outputPower"] = r.outputPower
    data["outputVoltage"] = r.outputVoltage
    data["outputCurrent"] = r.outputCurrent
    data["chargingMode"] = r.chargingMode
    data["chargingModeDesc"] = r.chargingModeDesc
    return data


# renogyhistory has two possable route structures depending on if the end of the time range is passed
# if only the start time is passed the current time is used as the end time
# Note: times are number of seconds since the start of the epoch
@app.route("/renogyhistory/<start>/<end>")
@app.route("/renogyhistory/<start>")
def renogyhistory(start=str(int(time.time())), end=str(int(time.time()))):
    sl = SolarLogger()
    log = sl.getLogData(int(start), int(end))
    data = {}
    logEntries = log.split("\n")
    for logEntry in logEntries:
        entryItems = logEntry.split("\t")
        if len(entryItems) >= 4:
            entryArray = [float(entryItems[1]), float(
                entryItems[2]), float(entryItems[3])]
            data[int(entryItems[0])] = entryArray
    return data
