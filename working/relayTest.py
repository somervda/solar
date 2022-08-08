import time
from solarrelay import SolarRelay
sr = SolarRelay()
sr.rigOn()
print("On")
time.sleep(15)
sr.rigOff()
print("off")
