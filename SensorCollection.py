from Adafruit_CCS811 import Adafruit_CCS811 as CCS
import smbus
import time
from sqlalchemy import Column, Numeric, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from base import Base, BaseRemote, BaseCombined


class Readings(Base):
    __tablename__ = 'readings'

    time = Column(String(250), primary_key=True)
    box_name = Column(String(250))
    FS = Column(Numeric)
    IS = Column(Numeric)
    VS = Column(Numeric)
    CO = Column(Numeric)
    TVOC = Column(Numeric)
    cTemp = Column(Numeric)
    fTemp = Column(Numeric)
    humidity = Column(Numeric)
    pressure = Column(Numeric)

    def __init__(self, time, box_name, FS, IS, VS, CO, TVOC, cTemp, fTemp, humidity, pressure):
        self.time = time
        self.box_name = box_name
        self.FS = FS
        self.IS = IS
        self.VS = VS
        self.CO = CO
        self.TVOC = TVOC
        self.cTemp = cTemp
        self.fTemp = fTemp
        self.humidity = humidity
        self.pressure = pressure


class ReadingsRemote(BaseRemote):
    __tablename__ = 'readings'

    time = Column(String(250), primary_key=True)
    box_name = Column(String(250))
    FS = Column(Numeric)
    IS = Column(Numeric)
    VS = Column(Numeric)
    CO = Column(Numeric)
    TVOC = Column(Numeric)
    cTemp = Column(Numeric)
    fTemp = Column(Numeric)
    humidity = Column(Numeric)
    pressure = Column(Numeric)

    def __init__(self, time, box_name, FS, IS, VS, CO, TVOC, cTemp, fTemp, humidity, pressure):
        self.time = time
        self.box_name = box_name
        self.FS = FS
        self.IS = IS
        self.VS = VS
        self.CO = CO
        self.TVOC = TVOC
        self.cTemp = cTemp
        self.fTemp = fTemp
        self.humidity = humidity
        self.pressure = pressure


class ReadingsCombined(BaseCombined):
    __tablename__ = 'readings'

    time = Column(String(250), primary_key=True)
    box_name = Column(String(250))
    FS = Column(Numeric)
    IS = Column(Numeric)
    VS = Column(Numeric)
    CO = Column(Numeric)
    TVOC = Column(Numeric)
    cTemp = Column(Numeric)
    fTemp = Column(Numeric)
    humidity = Column(Numeric)
    pressure = Column(Numeric)

    def __init__(self, time, box_name, FS, IS, VS, CO, TVOC, cTemp, fTemp, humidity, pressure):
        self.time = time
        self.box_name = box_name
        self.FS = FS
        self.IS = IS
        self.VS = VS
        self.CO = CO
        self.TVOC = TVOC
        self.cTemp = cTemp
        self.fTemp = fTemp
        self.humidity = humidity
        self.pressure = pressure


def Light():
    # Get I2C bus
    bus = smbus.SMBus(1)

    # TSL2561 address, 0x39(57)
    # Select control register, 0x00(00) with command register, 0x80(128)
    #		0x03(03)	Power ON mode
    bus.write_byte_data(0x39, 0x00 | 0x80, 0x03)
    # TSL2561 address, 0x39(57)
    # Select timing register, 0x01(01) with command register, 0x80(128)
    #		0x02(02)	Nominal integration time = 402ms
    bus.write_byte_data(0x39, 0x01 | 0x80, 0x02)

    time.sleep(0.5)

    # Read data back from 0x0C(12) with command register, 0x80(128), 2 bytes
    # ch0 LSB, ch0 MSB
    data = bus.read_i2c_block_data(0x39, 0x0C | 0x80, 2)
    # Read data back from 0x0E(14) with command register, 0x80(128), 2 bytes
    # ch1 LSB, ch1 MSB
    data1 = bus.read_i2c_block_data(0x39, 0x0E | 0x80, 2)

    # Convert the data
    ch0 = data[1] * 256 + data[0]
    ch1 = data1[1] * 256 + data1[0]
    ch2 = ch0 - ch1
    FS = ch0
    IS = ch1
    VS = ch2

    return FS, IS, VS


def Air():
    chip = CCS()
    CO = chip.geteCO2()
    TVOC = chip.getTVOC()

    return CO, TVOC


def Temp():
    # Get I2C bus
    bus = smbus.SMBus(1)

    # SHT31 address, 0x44(68)
    bus.write_i2c_block_data(0x45, 0x2C, [0x06])

    time.sleep(0.5)

    # SHT31 address, 0x44(68)
    # Read data back from 0x00(00), 6 bytes
    # Temp MSB, Temp LSB, Temp CRC, Humididty MSB, Humidity LSB, Humidity CRC
    data = bus.read_i2c_block_data(0x45, 0x00, 6)

    # Convert the data
    temp = data[0] * 256 + data[1]
    cTemp = -45 + (175 * temp / 65535.0)
    fTemp = -49 + (315 * temp / 65535.0)
    humidity = 100 * (data[3] * 256 + data[4]) / 65535.0

    return cTemp, fTemp, humidity


def Pressure():
    # Get I2C bus
    bus = smbus.SMBus(1)

    # BMP280 address, 0x76(118)
    # Read data back from 0x88(136), 24 bytes
    b1 = bus.read_i2c_block_data(0x77, 0x88, 24)

    # Convert the data
    # Temp coefficents
    dig_T1 = b1[1] * 256 + b1[0]
    dig_T2 = b1[3] * 256 + b1[2]
    if dig_T2 > 32767:
        dig_T2 -= 65536
    dig_T3 = b1[5] * 256 + b1[4]
    if dig_T3 > 32767:
        dig_T3 -= 65536

    # Pressure coefficents
    dig_P1 = b1[7] * 256 + b1[6]
    dig_P2 = b1[9] * 256 + b1[8]
    if dig_P2 > 32767:
        dig_P2 -= 65536
    dig_P3 = b1[11] * 256 + b1[10]
    if dig_P3 > 32767:
        dig_P3 -= 65536
    dig_P4 = b1[13] * 256 + b1[12]
    if dig_P4 > 32767:
        dig_P4 -= 65536
    dig_P5 = b1[15] * 256 + b1[14]
    if dig_P5 > 32767:
        dig_P5 -= 65536
    dig_P6 = b1[17] * 256 + b1[16]
    if dig_P6 > 32767:
        dig_P6 -= 65536
    dig_P7 = b1[19] * 256 + b1[18]
    if dig_P7 > 32767:
        dig_P7 -= 65536
    dig_P8 = b1[21] * 256 + b1[20]
    if dig_P8 > 32767:
        dig_P8 -= 65536
    dig_P9 = b1[23] * 256 + b1[22]
    if dig_P9 > 32767:
        dig_P9 -= 65536

    # BMP280 address, 0x76(118)
    # Select Control measurement register, 0xF4(244)
    #		0x27(39)	Pressure and Temperature Oversampling rate = 1
    #					Normal mode
    bus.write_byte_data(0x77, 0xF4, 0x27)
    # BMP280 address, 0x76(118)
    # Select Configuration register, 0xF5(245)
    #		0xA0(00)	Stand_by time = 1000 ms
    bus.write_byte_data(0x77, 0xF5, 0xA0)

    # BMP280 address, 0x76(118)
    # Read data back from 0xF7(247), 8 bytes
    # Pressure MSB, Pressure LSB, Pressure xLSB, Temperature MSB, Temperature LSB
    # Temperature xLSB, Humidity MSB, Humidity LSB
    data = bus.read_i2c_block_data(0x77, 0xF7, 8)

    # Convert pressure and temperature data to 19-bits
    adc_p = ((data[0] * 65536) + (data[1] * 256) + (data[2] & 0xF0)) / 16
    adc_t = ((data[3] * 65536) + (data[4] * 256) + (data[5] & 0xF0)) / 16

    # Temperature offset calculations
    var1 = ((adc_t) / 16384.0 - (dig_T1) / 1024.0) * (dig_T2)
    var2 = (((adc_t) / 131072.0 - (dig_T1) / 8192.0) * ((adc_t) / 131072.0 - (dig_T1) / 8192.0)) * (dig_T3)
    t_fine = (var1 + var2)
    cTemp = (var1 + var2) / 5120.0
    fTemp = cTemp * 1.8 + 32

    # Pressure offset calculations
    var1 = (t_fine / 2.0) - 64000.0
    var2 = var1 * var1 * (dig_P6) / 32768.0
    var2 = var2 + var1 * (dig_P5) * 2.0
    var2 = (var2 / 4.0) + ((dig_P4) * 65536.0)
    var1 = ((dig_P3) * var1 * var1 / 524288.0 + (dig_P2) * var1) / 524288.0
    var1 = (1.0 + var1 / 32768.0) * (dig_P1)
    p = 1048576.0 - adc_p
    p = (p - (var2 / 4096.0)) * 6250.0 / var1
    var1 = (dig_P9) * p * p / 2147483648.0
    var2 = p * (dig_P8) / 32768.0
    pressure = (p + (var1 + var2 + (dig_P7)) / 16.0) / 100

    return pressure
