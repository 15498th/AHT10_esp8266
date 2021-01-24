## AHT10_esp32
Micropython library for AHT10 humidity and temperature sensor.
Heavily based on [https://github.com/Thinary/AHT10](https://github.com/Thinary/AHT10).


## Usage

Measurement is triggered by calling `initiateMeasurement()`. It takes some time to complete the measurement, so data shouldn't be read from sensor memory before it is updated, otherwise it could be left in inconsistent state or contain values from previous reading. See status evaluation section below.
The sensor memory consists of 6 bytes. First byte is used for status bits and others are devided between temperature and humidity values. Sensor memory is read to internal buffer with `readRawData()` method and then converted to actual temperature and humidity values with `convertTemperature()` and `convertHumidity()` methods. 


```python
import time
from machine import I2C
import aht10.py

# Create i2c bus object, pins here are hardware i2c pins for ESP32
i2c = I2C(0, sda=Pin(21), scl=Pin(22))

# Create sensor object. Default address argument is 56 and can be ommited
sensor = aht10.AHT10(i2c=i2c, address=56)

# Tell sensor to do a single measurement
sensor.initiateMeasurement()

# Wait for sensor to complete measurement. It takes about 75 ms according to manual
time.sleep_ms(100)

# Read data from sensor memory to internal buffer
sensor.readRawData()

# Convert data from internal buffer to human readable format
# returns float
temperature = sensor.convertTemperature()
humidity = sensor.convertHumidity()
```

Reading property `values` combines all above:

```python
from machine import I2C
import aht10.py

i2c = I2C(0, sda=Pin(21), scl=Pin(22))
sensor = aht10.AHT10(i2c=i2c)

# returns str
humidity, temperature = sensor.values
```

## Status evaluation

Status byte is used to determine current state of device.


`statusBusy()` used to check if last measurement is done and data can be read. After `initiateMeasurement()` is called, sensor needs some time to complete conversion. Before that `statusBusy()` will return `true`. Reading data in busy state in most cases would get values from previous measurement, but can result in something else, like returning unrealistic values after `reset()`.

```python
sensor.initiateMeasurement()
while(sensor.statusBusy()):
    time.sleep_ms(10)
sensor.readRawData()
```

Minimum recommended reading rate of this sensor is once in two seconds, so in general case it's better to just wait until device has enough time to complete measurement instead of actively monitoring busy state.


Calibration coefficient is loaded with `calibrate()` and checked with `statusCalibrated()` method.

```python
if not sensor.statusCalibrated():
    sensor.calibrate()
```

