import time
from solarrelay import SolarRelay
sr = SolarRelay()
sr.rigOn()
print("On")
time.sleep(5)
sr.rigOff()
print("off")
