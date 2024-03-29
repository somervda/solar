import socket
from tokenize import Number
from flask import Flask, jsonify
from renogy import Renogy
from solarlogger import SolarLogger
from solarrelay import SolarRelay
from solarcache import SolarCache
import settings
import time
from datetime import datetime


app = Flask(__name__)


def netcat(host, port, content):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, int(port)))
    s.sendall(content.encode())
    s.shutdown(socket.SHUT_WR)
    while True:
        data = s.recv(4096)
        if not data:
            break
        return data
    s.close()


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


# renogyhistory has three possible route structures depending on what parameters are passed
# No parameters will return last 24 hours of data
# One parameter - will return data starting from the time (epoch seconds) passed
# two parameters - will return data starting from the first time and ending at the second
# Note: times are number of seconds since the start of the epoch
# e.g. http://<host>/solar/renogyhistory/<start>/<end>
@app.route("/renogyhistory/<start>/<end>")
@app.route("/renogyhistory/<start>")
@app.route("/renogyhistory")
def renogyhistory(start=0, end=0):
    # Check the start and end values are integers
    try:
        _start = int(start)
        _end = int(end)
    except:
        return "Start/End values not integer(s).", 400
    if start == 0:
        start = (time.time() - (24 * 60 * 60))
    if end == 0:
        end = time.time()
    with open("/home/pi/solar/logs/solarwww.log", "a") as logging_file:
        logging_file.write("{} start:{} end:{}\n".format(
            datetime.now(), start, end))
    sl = SolarLogger()
    log = sl.getLogData(int(start), int(end))
    # Convert the data from getLogData (Tab delimited) to a dictionary object
    data = []
    logEntries = log.split("\n")
    for logEntry in logEntries:
        entryItems = logEntry.split("\t")
        if len(entryItems) >= 4:
            entryArray = [int(entryItems[0]), float(entryItems[1]), float(entryItems[2]), float(
                entryItems[3])]
            data.append(entryArray)
    # flask converts dictionary objects to json
    return jsonify(data)


@app.route("/panelhistory/<start>/<end>")
@app.route("/panelhistory/<start>")
@app.route("/panelhistory")
def panelhistory(start=0, end=0):
    # Check the start and end values are integers
    try:
        _start = int(start)
        _end = int(end)
    except:
        return "Start/End values not integer(s).", 400
    if start == 0:
        start = (time.time() - (24 * 60 * 60))
    if end == 0:
        end = time.time()
    with open("/home/pi/solar/logs/solarwww.log", "a") as logging_file:
        logging_file.write("{} start:{} end:{}\n".format(
            datetime.now(), start, end))
    sl = SolarLogger()
    log = sl.getLogData(int(start), int(end))
    # Convert the data from getLogData (Tab delimited) to a dictionary object
    data = []
    logEntries = log.split("\n")
    for logEntry in logEntries:
        entryItems = logEntry.split("\t")
        if len(entryItems) == 8:
            # entryArray = [int(entryItems[0])]
            entryArray = [int(entryItems[0]), float(entryItems[5]), float(
                entryItems[6]), float(entryItems[7])]
            data.append(entryArray)
            # data[int(entryItems[0])] = entryArray
    # flask converts dictionary objects to json
    return jsonify(data)


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
        rigState = sr.rigOn(True)
        if rigState == "":
            return ""
        else:
            return rigState, 400
    else:
        sr.rigOff()
        return ""


@app.route("/mumble/<state>")
def mumble(state):
    if not (state == "on" or state == "off"):
        return "Mumble value must be on or off", 400
    sr = SolarRelay()
    if state == "on":
        mumbleState = sr.mumbleOn()
        if mumbleState == "":
            return ""
        else:
            return mumbleState, 400
    else:
        sr.mumbleOff()
        return ""


@app.route("/mumble")
def mumbleState():
    sr = SolarRelay()
    return sr.getMumbleState()


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


@app.route("/rigctl/<operation>")
def rigctl(operation=""):
    try:
        # return netcat("127.0.0.1", 4532, "\\" + operation).decode("utf-8"), 200, {'Content-Type': 'text/plain; charset=utf-8'}
        return netcat(settings.HOST, 4532, "\\" + operation).decode("utf-8"), 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except Exception as e:
        return "rigctl failed:", 500
