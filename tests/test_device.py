# Reading from a EasyLap device.

from easylap import EasyLapDevice

easylap = EasyLapDevice()
easylap.receive(lambda t, c: print('t: {}, c: {}'.format(t, c))) 