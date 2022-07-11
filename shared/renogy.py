# The renogy class manages the interface to a renogy solar controller.
# this includes the modbus and rs232 functionality as well as
# exposing the renogy data in a single namespace.

from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.transaction import ModbusRtuFramer


class Renogy:
    def __init__(self):
        # Set up properties to be retrieved from the renogy solar controller
        self.batteryVoltage = 0
        self.batteryCapacity = 0
        self.solarVolts = 0
        self.solarAmps = 0
        self.solarPower = 0
        self.outputVoltage = 0
        self.outputCurrent = 0
        self.outputPower = 0
        self.chargingMode = 0
        self.chargingModeDesc = ""
        self.modbus = ModbusClient(method='rtu', port='/dev/serial0', baudrate=9600,
                                   stopbits=1, bytesize=8, parity='N', timeout=5, unit=1)
        # Get the first set of data
        self.refresh()

    def refresh(self):
        self.modbus.connect()
        r = self.modbus.read_holding_registers(0x100, 35, unit=1)
        # print(r.registers)
        self.batteryVoltage = r.registers[0x1]/10
        self. batteryCapacity = r.registers[0x0]
        self.solarVolts = r.registers[0x7]/10
        self.solarAmps = float(r.registers[0x8])/100
        # self.solarPower = r.registers[0x9]
        self.solarPower = round(self.solarVolts * self.solarAmps, 3)
        self.outputVoltage = r.registers[0x4]/10
        self.outputCurrent = r.registers[0x5]/100
        self.outputCurrent -= .085
        self.outputPower = round(self.outputVoltage*self.outputCurrent, 3)
        self.chargingMode = r.registers[0x20].to_bytes(2, byteorder="big")[1]
        if self.chargingMode == 0:
            self.chargingModeDesc = 'Charging Deactivated'
        elif self.chargingMode == 1:
            self.chargingModeDesc = 'Charging Activated'
        elif self.chargingMode == 2:
            self.chargingModeDesc = 'MPPT Charging Mode'
        elif self.chargingMode == 3:
            self.chargingModeDesc = 'Equilizing Charging Mode'
        elif self.chargingMode == 4:
            self.chargingModeDesc = 'Boost Charging Mode'
        elif self.chargingMode == 5:
            self.chargingModeDesc = 'Floating Charging Mode'
        elif self.chargingMode == 6:
            self.chargingModeDesc = 'Current Limiting Charging Mode'
        else:
            self.chargingModeDesc = "Charging Mode {}".format(
                str(chargingMode))

        self.modbus.close()
