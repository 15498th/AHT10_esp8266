import time

AHT10_I2CADDR = 56
CalibrateCmd = b'\xE1\x08\x00'
NormalCmd = b'\xA8\x00\x00'
MeasureCmd = b'\xAC\x33\x00'
ResetCmd = b'\xBA'

class AHT10:

    def __init__(self,address=AHT10_I2CADDR,i2c=None):
        if i2c is None:
            raise ValueError('An I2C object is required.')
        self.i2c = i2c
        self.address = address
        self.reset()
        self.raw_data = bytearray(6)

    def readStatus(self, from_buffer=False):
        if from_buffer:
            status = self.raw_data[0]
        else:
            status = self.i2c.readfrom(self.address, 1)[0]
        return status

    def initiateMeasurement(self):
        self.i2c.writeto(self.address, MeasureCmd)

    def reset(self):
        self.i2c.writeto(self.address, ResetCmd)

    def calibrate(self):
        self.i2c.writeto(self.address, CalibrateCmd)

    def readRawData(self):
        self.raw_data = self.i2c.readfrom(self.address, 6)

    def convertHumidity(self):
        raw_humidity = ((self.raw_data[1] << 16) | (self.raw_data[2] << 8) | self.raw_data[3]) >> 4
        return raw_humidity * 100 / 1048576

    def convertTemperature(self):
        raw_temperature = ((self.raw_data[3] & 0x0F) << 16) | (self.raw_data[4] << 8) | self.raw_data[5]
        return ((200 * raw_temperature) / 1048576) - 50

    def readAndConvert(self):
        self.initiateMeasurement()
        time.sleep_ms(100) 
        self.readRawData()
        hum = self.convertHumidity()
        temp = self.convertTemperature()
        return [hum, temp]

    def statusCalibrated(self, from_buffer=False):
        status = self.readStatus(from_buffer)
        return self.bitIsSet(status,3)

    def statusBusy(self, from_buffer=False):
        status = self.readStatus(from_buffer)
        return self.bitIsSet(status,7)

    def statusMode(self, from_buffer=False):
        status = self.readStatus(from_buffer)
        if (self.bitIsSet(status,6)):
            return 'CMD'
        elif (self.bitIsSet(status,5)):
            return 'CYC'
        else:
            return 'NOR'

    def bitIsSet(self, byte, bit):
        if (byte & (1<<bit) == 0 ):
            return False
        else:
            return True

    @property
    def values(self):
        """ human readable values """

        h, t = self.readAndConvert()
        return ("{:.2f}".format(t), "{:.2f}".format(h))
