from solarlogger import SolarLogger
import time

sl = SolarLogger()
start = (time.time() - (24 * 60 * 60))
end = time.time()

print("start:{}".format(start))
print("end:{}".format(end))
print(sl.getLogData(int(start), int(end)))
