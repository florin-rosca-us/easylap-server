# Copyright 2019 Robert Ginda <rginda@gmail.com>
# This code is licensed under MIT license (see LICENSE.md for details)
#

"""
Python library to interface with Robotronic/Easylap USB compatible r/c car lap
counters.

See https://github.com/rginda/pycp2110

Modified to accept/ignore garbage from cp2110 
Use the aiodevice module instead of this for asynchronous operations.

"""

import sys
from .base import Base, LogOptions

try:
  from cp2110 import CP2110Device, UARTConfig, PARITY, FLOW_CONTROL, DATA_BITS, STOP_BITS, RX_TX_MAX
except ImportError:
  try:
    from .fake.cp2110 import *
  except ImportError as e:
    print('Cannot import: {} - exiting.'.format(e))
    sys.exit(1)
    
   

class EasyLapDeviceException(Exception):
  def __init__(self, wrapped):
    self.wrapped = wrapped
    super().__init__()
     

class EasyLapDevice(Base):
  
  EASYLAP_PID = 0x86B9
  
  
  def __init__(self, log_options = LogOptions()):
    super().__init__('EasyLapDevice', log_options)
  
  
  def receive(self, callback):
    """ Receives from a EasyLap device.
    
    :param callback: the callback called when data is received.
    
    """
    if not callback:
      raise RuntimeError('A callback is required')
    
    # Main loop
    d = CP2110Device(pid=self.EASYLAP_PID)
    d.set_uart_config(UARTConfig(
      baud=38400, parity=PARITY.NONE, flow_control=FLOW_CONTROL.DISABLED,
      data_bits=DATA_BITS.EIGHT, stop_bits=STOP_BITS.SHORT))
    d.enable_uart()
  
    buf = []
  
    while True:
      chunk = d.read(RX_TX_MAX + 1)
      while chunk:
        buf += chunk
        time.sleep(0.025)
        chunk = d.read(RX_TX_MAX + 1)
        
      if not buf:
        time.sleep(0.025)
        continue
  
      # print(['%.2X' % int(x) for x in buf])
  
      if buf[0] == 0x0B: # Timer packet
        if len(buf) >= 3 and buf[2] != 0x83: # garbage? discard one
          buf = buf[1:]
        elif len(buf) >= 0x0B: # 11 bytes
          timer_value = (buf[3] | buf[4] << 8 | buf[5] << 16 | buf[6] << 32)
          # print("timer: %s" % timer_value)
          callback(t = timer_value, c = None)
          buf = buf[0x0B + 1:]
           
      elif buf[0] == 0x0D: # Car packet
        if len(buf) >= 3 and buf[2] != 0x84: # garbage? discard one
          buf = buf[1:]
        elif len(buf) >= 0x0D: # 13 bytes
          uid = (buf[3] | buf[4] << 8)
          timer_value = (buf[7] | buf[8] << 8 | buf[9] << 16 | buf[10] << 32)
          # print("car: %s: %s" % (uid, timer_value))
          callback(t = timer_value, c = uid)
          buf = buf[0x0D + 1:]
      
      else:  
        buf = buf[1:]

  