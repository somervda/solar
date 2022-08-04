import time
from solarrelay import SolarRelay
sr = SolarRelay()
sr.rigOn()
print("On")
time.sleep(30)
sr.rigOff()
print("off")
