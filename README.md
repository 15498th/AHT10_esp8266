## AHT10_esp8266
Micropython library for AHT10 humidity and temperature sensor.
Adapted from [https://github.com/15498th/AHT10_esp32](https://github.com/15498th/AHT10_esp32) to use less memory by cost of changing interface and ommiting some methods.
I2C initialization is performed by calling code, so module should work on esp32 as well.


## Usage

Measurement is triggered by calling `initiateMeasurement()`. It takes some time to complete the measurement, so data shouldn't be read from sensor memory before it is updated, otherwise it could be left in inconsistent state or contain values from previous reading. See status evaluation section below.
The sensor memory consists of 6 bytes. First byte is used for status bits and others are devided between temperature and humidity values. Sensor memory is read to internal buffer and converted to actual temperature and humidity values with `readData()` method. Converted values are stored in `AHT10.temperature` and `AHT10.humidity` fields.


```python
import time
from machine import I2C
import aht10.py

# Create i2c bus object, pins here are hardware i2c pins for ESP8266
i2c = I2C(sda=Pin(4), scl=Pin(5))

# Create sensor object. Default address argument is 56 and can be ommited
sensor = aht10.AHT10(i2c=i2c, address=56)

# Tell sensor to do a single measurement
sensor.initiateMeasurement()

# Wait for sensor to complete measurement. It takes about 75 ms according to manual
time.sleep_ms(100)

# Read data from sensor memory to internal buffer
sensor.readData()

# Print measured data:
template = 'temperature: {:.2f}, humidity: {:.2f}'
print(template.format(sensor.temperature, sensor.humidity))
```

## Status evaluation

After `initiateMeasurement()` is called, sensor needs some time to complete conversion. Reading data before that in most cases would get values from previous measurement, but can result in something else, like returning unrealistic values right after initialization.

Status byte is used to determine current state of device.

To get actual value of status byte without reading whole device memory `readStatus()` is used. When conversion is completed, seventh bit of status is set to `1`.


```python
sensor.initiateMeasurement()
while(sensor.readStatus() & (1<<7)):
    time.sleep_ms(10)
sensor.readRawData()
```

Consult sensor manual for meaning of other bits.

Minimum recommended reading rate of this sensor is once in two seconds, so in general case it's better to just wait until device had enough time to complete measurement instead of actively monitoring busy state.
Performing measurement at faster rate might cause sensor to self-heat, which adds error to measurement.

