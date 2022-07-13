# This class abstracts away how power usage logging is performed.
# You can call it to log a specific hours data (Currently solar power generated, used, and battery % )
# For now will store as daily log files but can change to something more
# sophisticated if I need to

import time
from os.path import exists


class SolarLogger:
    def __init__(self):
        self.loggingDirectory = "/home/pi/solar/logs/"

    def writeData(self, batteryCapacity, solarPower, outputPower, modeNC, modeBulk, modeBoost, modeFloat, modeEql, modeOther):
        # writes a record to the current days log
        timeNow = time.time()
        timeGMT = time.gmtime(timeNow)
        logEntry = "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
            round(timeNow), batteryCapacity, solarPower, outputPower, modeNC, modeBulk, modeBoost, modeFloat, modeEql, modeOther)
        # Write the entry to the log file for the day
        fn = "{}solar{:04d}{:02d}{:02d}.tab".format(
            self.loggingDirectory, timeGMT.tm_year,  timeGMT.tm_mon,  timeGMT.tm_mday)
        with open(fn, "a") as logging_file:
            logging_file.write(logEntry)

    def getLogData(self, begin, end=int(time.time()), convertToLocalTime=False, convertToCSV=False, addSeriesNames=False):
        # Will get all the data between two times
        # by default will return an array of hourly values starting at begin time (seconds since epoch)

        # Get the files needed and merge all the data together
        entries = ""
        if addSeriesNames:
            entries = "Time\tBattery %\tSolar Wh\tLoad Wh\tmodeNC\tmodeBulk\tmodeBoost\tmodeFloat\tmodeEql\tmodeOther\n"
        # Need to start looking for files from first minute of the begin day
        # print("begin:{} end:{}".format(begin,end))
        startOfBeginDay = begin - \
            (time.gmtime(begin).tm_hour * 60 * 60) - \
            (time.gmtime(begin).tm_min * 60) + 60
        for filedate in range(startOfBeginDay, end, (60*60*24)):
            fn = "{}solar{:04d}{:02d}{:02d}.tab".format(
                self.loggingDirectory, time.gmtime(filedate).tm_year, time.gmtime(filedate).tm_mon, time.gmtime(filedate).tm_mday)
            # print("fn:" + fn + " fileDate:" + str(time.gmtime(filedate)))
            if exists(fn):
                with open(fn, "r") as logging_file:
                    # filter out entries that are not in required range
                    lines = logging_file.readlines()
                    for line in lines:
                        values = line.split("\t")
                        if float(values[0]) >= begin and float(values[0]) <= end:
                            if convertToLocalTime:
                                newLine = ""
                                # update epoch based to to a local user readable time
                                values[0] = time.strftime("%x %X", time.localtime(
                                    float(values[0])))
                                for n in range(len(values)):
                                    newLine += values[n]
                                    if n < len(values)-1:
                                        newLine += "\t"
                                    # else:
                                    #     newLine += "\n"
                                line = newLine
                                # print("*" + newLine + "*")

                            entries += line
        if convertToCSV:
            entries = entries.replace('\t', ',')
        return entries
