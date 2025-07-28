#!/usr/bin/python3 
# -*- coding: utf-8 -*-

from bme280 import bme280
from bme280 import bme280_i2c
from bme280.bme280 import read_all

bme280_i2c.set_default_i2c_address(int("0x77", 0)) # address of sensor 0x77
bme280_i2c.set_default_bus(2) # depends on distro version
bme280.setup() 

data = bme280.read_all()

print(("{}\t{}\t{}".format(data.pressure, data.humidity, data.temperature)))
