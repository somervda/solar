from solarlogger import SolarLogger

sl = SolarLogger()
# sl.writeData(50, 9, 8)
print(sl.getLogData(1657558800, convertToLocalTime=True,
      convertToCSV=True, addSeriesNames=True))
