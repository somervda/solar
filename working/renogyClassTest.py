#  make sure shared folder is on your PYTHONPATH
from renogy import Renogy
import datetime

#  Make a new instance of the Renogy class from the renogy module
r=Renogy()
# Display the data Note: Do a refresh() to update the data
print(datetime.datetime.now())
print('Battery Capacity {}%'.format(str(r.batteryCapacity)))
print('Battery Voltage {}V'.format(str(r.batteryVoltage)))
print('Solar Amps {}A'.format(str(r.solarAmps)))
print('Solar Volts {}V'.format(str(r.solarVolts)))
print('Solar Power {}W'.format(str(r.solarPower)))
print('Output Power {}W'.format(str(round(r.outputPower, 3))))
print('Output Voltage {}V'.format(str(r.outputVoltage)))
print('Output Current {}A'.format(str(round(r.outputCurrent, 3))))
print(r.chargingModeDesc)