from solarlogger import SolarLogger

sl = SolarLogger()
sl.writeData(50, 9, 8)
print(sl.getLogData(1657400101, 1657400743))
