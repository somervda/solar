from flask import Flask
from renogy import Renogy

app = Flask(__name__)


@app.route("/renogy")
def getRenogy():
    r = Renogy()
    data = {}
    data["batteryCapacity"] = r.batteryCapacity
    data["solarPower"] = r.solarPower
    data["outputPower"] = r.outputPower
    return data
