import time
from solarrelay import SolarRelay
sr = SolarRelay()
out=sr.rigOn()
print("On:",out)
# time.sleep(15)
# sr.rigOff()
# print("off")
