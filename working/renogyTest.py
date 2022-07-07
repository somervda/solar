# Import Pymodbus
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.transaction import ModbusRtuFramer
# Create ModbusClient instance and connect
# External board for ttl to serial, connected to solar charge controller
modbus = ModbusClient(method='rtu', port='/dev/serial0', baudrate=9600,
                      stopbits=1, bytesize=8, parity='N', timeout=5, unit=1)
a = modbus.connect()
# Get basic renogy wanderer controller status
# See https://docs.google.com/document/d/1OSW3gluYNK8d_gSz4Bk89LMQ4ZrzjQY6/edit
# Renogy Wanderer 10A Manual https://www.renogy.com/content/RNG-CTRL-WND10/WND10-Manual.pdf
print("Current Controller Status")
r = modbus.read_holding_registers(0x100, 35, unit=1)
print(r.registers)
batteryVoltage = r.registers[0x1]/10
batteryCapacity = r.registers[0x0]
solarVolts = r.registers[0x7]/10
solarAmps = float(r.registers[0x8])/100
solarPower = r.registers[0x9]
outputVoltage = r.registers[0x4]/10
outputCurrent = r.registers[0x5]/100
outputCurrent -= .085
outputPower = outputVoltage*outputCurrent
minBattVoltageToday = r.registers[0x0B]/10
maxBattVoltageToday = r.registers[0x0C]/10
totalDayPowerGenWh = r.registers[0x13]/10
totalDayPowerUsedWh = r.registers[0x14]/10
totalDayChargingAh = r.registers[0x11]
totalDayDischargingAh = r.registers[0x12]
chargingMode = r.registers[0x20].to_bytes(2, byteorder="big")[1]

print('Battery Capacity {}%'.format(str(batteryCapacity)))
print('Battery Voltage {}V'.format(str(batteryVoltage)))
print('Solar Amps {}A'.format(str(solarAmps)))
print('Solar Volts {}V'.format(str(solarVolts)))
print('Solar Power {}W'.format(str(solarPower)))
print('Output Power {}W'.format(str(round(outputPower, 3))))
print('Output Voltage {}V'.format(str(outputVoltage)))
print('Output Current {}A'.format(str(round(outputCurrent, 3))))
print('')
print('Total Power Gen today {}Wh'.format(str(totalDayPowerGenWh)))
print('Total Power Used today {}Wh'.format(str(totalDayPowerUsedWh)))
print('Charging today {}Ah'.format(str(totalDayChargingAh)))
print('Discharging today {}Ah'.format(str(totalDayDischargingAh)))
print('Min. battery voltage today {}V'.format(str(minBattVoltageToday)))
print('Max. battery voltage today {}V'.format(str(maxBattVoltageToday)))
if chargingMode == 0:
    print('Charging Deactivated')
elif chargingMode == 1:
    print('Charging Activated')
elif chargingMode == 2:
    print('MPPT Charging Mode')
elif chargingMode == 3:
    print('Equilizing Charging Mode')
elif chargingMode == 4:
    print('Boost Charging Mode')
elif chargingMode == 5:
    print('Floating Charging Mode')
elif chargingMode == 6:
    print('Current Limiting Charging Mode')
else:
    print("Charging Mode {}".format(str(chargingMode)))
