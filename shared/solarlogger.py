# This class abstracts away how power usage logging is performed.
# You can call it to log a specific hours data (Currently solar power generated, used, and battery % )
# For now will store as daily log files but can change to something more
# sophisticated if I need to

import time
from os.path import exists


class SolarLogger:
    def __init__(self):
        self.loggingDirectory = "../logs/"

    def writeData(self, batteryCapacity, solarPower, outputPower):
        # writes a record to the current days log
        timeNow = time.time()
        timeGMT = time.gmtime(timeNow)
        logEntry = "{}\t{}\t{}\t{}\n".format(
            round(timeNow), batteryCapacity, solarPower, outputPower)
        # Write the entry to the log file for the day
        fn = "{}solar{:04d}{:02d}{:02d}.tab".format(
            self.loggingDirectory, timeGMT.tm_year,  timeGMT.tm_mon,  timeGMT.tm_mday)
        with open(fn, "a") as logging_file:
            logging_file.write(logEntry)

    def getLogData(self, begin, end=int(time.time())):
        # Will get all the data between two times
        # by default will return an array of hourly values starting at begin time (seconds since epoch)

        # Get the files needed and merge all the data together
        entries = ""
        for filedate in range(begin, end, (60*60*24)):
            fn = "{}solar{:04d}{:02d}{:02d}.tab".format(
                self.loggingDirectory, time.gmtime(filedate).tm_year, time.gmtime(filedate).tm_mon, time.gmtime(filedate).tm_mday)
            if exists(fn):
                with open(fn, "r") as logging_file:
                    # filter out entries that are not in required range
                    lines = logging_file.readlines()
                    for line in lines:
                        values = line.split("\t")
                        if float(values[0]) >= begin and float(values[0]) <= end:
                            entries += line
        return entries
