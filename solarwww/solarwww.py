from flask import Flask
from renogy import Renogy
from solarlogger import SolarLogger
from solarrelay import SolarRelay
from solarcache import SolarCache
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
    # flask converts dictionary objects to json
    return data


# renogyhistory has three possable route structures depending on what parameters are passed
# No parameters will return last 24 hours of data
# One parameter - will return data starting from the time (epoch seconds) passed
# two parameters - will return data starting from the first time and ending at the second
# Note: times are number of seconds since the start of the epoch
# e.g. http://<host>/solar/renogyhistory/<start>/<end>
@app.route("/renogyhistory/<start>/<end>")
@app.route("/renogyhistory/<start>")
@app.route("/renogyhistory")
def renogyhistory(start=(time.time() - (24 * 60 * 60)), end=time.time()):
    sl = SolarLogger()
    log = sl.getLogData(int(start), int(end))
    # Convert the data from getLogData (Tab delimited) to a dictionary object
    data = {}
    logEntries = log.split("\n")
    for logEntry in logEntries:
        entryItems = logEntry.split("\t")
        if len(entryItems) >= 4:
            entryArray = [float(entryItems[1]), float(
                entryItems[2]), float(entryItems[3])]
            data[int(entryItems[0])] = entryArray
    # flask converts dictionary objects to json
    return data


@app.route("/webcam/<state>")
def webcam(state="off"):
    sr = SolarRelay()
    result = "Unsuccessful"
    if state == "on":
        sr.webcamOn(True)
        result = "Webcam is On"
    if state == "off":
        sr.webcamOff()
        result = "Webcam is Off"
    return result


@app.route("/rig/<state>")
def rig(state="off"):
    sr = SolarRelay()
    result = "Unsuccessful"
    if state == "on":
        sr.rigOn(True)
        result = "Rig is On"
    if state == "off":
        sr.rigOff()
        result = "Rig is Off"
    return result


@app.route("/cache")
def cache():
    sc = SolarCache()
    data = {}
    data["powerSaveLevel"] = sc.powerSaveLevel
    data["webcamRunAtNight"] = sc.webcamRunAtNight
    data["webcamTurnOffTime"] = sc.webcamTurnOffTime
    data["webcamExpiryMinutes"] = sc.webcamExpiryMinutes
    data["webcamExpiry"] = sc.webcamExpiry
    data["webcamOn"] = sc.webcamOn
    data["rigExpiryMinutes"] = sc.rigExpiryMinutes
    data["rigExpiry"] = sc.rigExpiry
    data["rigOn"] = sc.rigOn
    # flask converts dictionary objects to json
    return data
