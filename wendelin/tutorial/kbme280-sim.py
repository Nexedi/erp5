#!/usr/bin/python3
# simulate bme280 from https://wendelin.nexedi.com/wendelin-Tutorial.Setup.Fluentd.on.Sensor
from random import gauss as g

Pm, Ps = 760, 30
Hm, Hs =  80, 5
Tm, Ts =  20, 2
print('%.1f\t%.1f\t%.1f' % (g(Pm,Ps), g(Hm,Hs), g(Tm,Ts)))
