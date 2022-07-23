from flask import Flask
from renogy import Renogy
from solarlogger import SolarLogger
from solarrelay import SolarRelay
from solarcache import SolarCache
import time
from datetime import datetime


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
    # Check the start and end values are integers
    try:
        _start = int(start)
        _end = int(end)
    except:
        return "Start/End values not integer(s).", 400
    with open("/home/pi/solar/logs/solarwww.log", "a") as logging_file:
        logging_file.write("{} start:{} end:{}\n".format(
            datetime.now(), start, end))
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
def webcam(state):
    if not (state == "on" or state == "off"):
        return "Webcam value must be on or off", 400
    sr = SolarRelay()
    if state == "on":
        sr.webcamOn(True)
    if state == "off":
        sr.webcamOff()
    return ""


@app.route("/rig/<state>")
def rig(state):
    if not (state == "on" or state == "off"):
        return "Rig value must be on or off", 400
    sr = SolarRelay()
    if state == "on":
        sr.rigOn(True)
    if state == "off":
        sr.rigOff()
    return ""


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

# Cache variables update services


@app.route("/cache/powerSaveLevel/<value>")
def powerSaveLevel(value):
    # Check the value is an integer
    try:
        _value = int(value)
    except:
        return "Value is not integer.", 400
    if _value < 0 or _value > 100:
        return "Invalid Value: Must be 0-100", 400
    sc = SolarCache()
    sc.powerSaveLevel = _value
    sc.writeCache()
    return ""


@app.route("/cache/webcamTurnOffTime/<value>")
def webcamTurnOffTime(value):
    sc = SolarCache()
    if value == "None":
        # Special value to reset the value
        sc.webcamTurnOffTime = None
        sc.writeCache()
        return ""
    # Check the value is an integer
    try:
        _value = int(value)
    except:
        return "Value is not integer.", 400
    if _value < 0 or (_value > 6 and _value < 18) or _value > 23:
        return "Invalid Value: Must be an hour between 6PM and 6AM (18-23 or 0-6)", 400
    sc.webcamTurnOffTime = _value
    sc.writeCache()
    return ""


@app.route("/cache/webcamRunAtNight/<value>")
def webcamRunAtNight(value):
    sc = SolarCache()
    if not (value == "True" or value == "False"):
        return "Value is not True or False.", 400
    if value == "True":
        sc.webcamRunAtNight = True
    else:
        sc.webcamRunAtNight = False
    sc.writeCache()
    return ""


@app.route("/cache/webcamExpiryMinutes/<value>")
def webcamExpiryMinutes(value):
    # Check the value is an integer
    try:
        _value = int(value)
    except:
        return "Value is not integer.", 400
    if _value <= 0 or _value > 180:
        return "Invalid Value: Must be 1-180 minutes", 400
    sc = SolarCache()
    sc.webcamExpiryMinutes = _value
    sc.writeCache()
    return ""


@app.route("/cache/rigExpiryMinutes/<value>")
def rigExpiryMinutes(value):
    # Check the value is an integer
    try:
        _value = int(value)
    except:
        return "Value is not integer.", 400
    if _value <= 0 or _value > 180:
        return "Invalid Value: Must be 1-180 minutes", 400
    sc = SolarCache()
    sc.rigExpiryMinutes = _value
    sc.writeCache()
    return ""
