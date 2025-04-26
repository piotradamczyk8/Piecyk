import pymodbus
import math
import time
from pymodbus import FramerType
from pymodbus.client import ModbusSerialClient

class PZEM_004T:
    voltage = 240
    current = 2
    power = 200
    energy = 2000
    frequency = 50    

    def __init__(self, port='/dev/ttyAMA0', baudrate=9600, timeout=1):
        self.client = ModbusSerialClient(
            port=port,
            framer=FramerType.RTU,            
            baudrate=baudrate,
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=timeout            
        )
        self.connection = self.client.connect()
        
        if self.connection:            
            print("Connected to PZEM-004T")
            time.sleep(1)            
            set_comunication_address = [0xB4, 0xC0, 0xA8, 0x01, 0x01, 0x00, 0x1E]
            voltage_read = [0xB0, 0xC0, 0xA8, 0x01, 0x01, 0x00, 0x1A]
            current_read = [0xB1, 0xC0, 0xA8, 0x01, 0x01, 0x00, 0x1B]
            power_read = [0xB2, 0xC0, 0xA8, 0x01, 0x01, 0x00, 0x1C]
            energy_read = [0xB3, 0xC0, 0xA8, 0x01, 0x01, 0x00, 0x1D]
            frequency_read = [0xB4, 0xC0, 0xA8, 0x01, 0x01, 0x00, 0x1E]
            #self.client.send(voltage_read)

    def reset_energy(self):
        # Reset energy count
        # 0x01 Slave address
        # 0x42 Magic code
        # 0x80 CRC for slave address (0x01)
        # 0x11 CRC for magic code (0x42)         
        data = [0x01, 0x42, 0x80, 0x11]
        time.sleep(2)

    def read_data(self):
        result = self.client.read_input_registers(0x00, count=10, slave=1)
        self.voltage = self.calc(result.registers[0:1], 10)
        self.current = self.calc(result.registers[1:3], 1000)
        self.power = self.calc(result.registers[3:5], 10)
        self.energy = self.calc(result.registers[5:7], 1)
        self.frequency = self.calc(result.registers[7:8], 10)
        self.power_factor = self.calc(result.registers[8:9], 100)
        self.alarm = self.calc(result.registers[9:10], 1)

    def get_voltage(self):
        return float(self.voltage)

    def set_voltage(self, value):
        self.voltage = value

    def get_current(self):
        return float(self.current)

    def set_current(self, value):
        self.current = value

    def get_power(self):
        return float(self.power)

    def set_power(self, value):
        self.power = value

    def get_energy(self):
        return int(self.energy)

    def set_energy(self, value):
        self.energy = value

    def get_frequency(self):
        return float(self.frequency)

    def set_frequency(self, value):
        self.frequency = value

    def get_power_factor(self):
        return self.power_factor

    def set_power_factor(self, value):
        self.power_factor = value

    def get_alarm(self):
        return self.alarm

    def set_alarm(self, value):
        self.alarm = value

    @staticmethod
    def calc(registers, factor):
        format = '%%0.%df' % int(math.ceil(math.log10(factor)))
        if len(registers) == 1:
            return format % ((1.0 * registers[0]) / factor)
        elif len(registers) == 2:
            return format % (((1.0 * registers[1] * 65535) + (1.0 * registers[0])) / factor)