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
        self.i2c.writeto(self.address, ResetCmd)
        self.raw_data = bytearray(6)
        self.raw_temperature = 0
        self.raw_humidity = 0
        self.temperature = 0.0
        self.humidity = 0.0

    def readStatus(self, from_buffer=False):
        if from_buffer:
            status = self.raw_data[0]
        else:
            status = self.i2c.readfrom(self.address, 1)[0]
        return status

    def initiateMeasurement(self):
        self.i2c.writeto(self.address, MeasureCmd)

    def readData(self):
        self.raw_data = self.i2c.readfrom(self.address, 6)
        raw_humidity = ((self.raw_data[1] << 16) | (self.raw_data[2] << 8) | self.raw_data[3]) >> 4
        self.humidity = raw_humidity * 100 / 1048576

        raw_temperature = ((self.raw_data[3] & 0x0F) << 16) | (self.raw_data[4] << 8) | self.raw_data[5]
        self.temperature = ((200 * raw_temperature) / 1048576) - 50

