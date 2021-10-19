# Fake cp2110 module that returns test data.
# Useful on Mac where cp2110 does not work:
# ImportError: Unable to load any of the following libraries: libhidapi-hidraw.so ...

import time
from enum import IntEnum, unique

@unique
class PARITY(IntEnum):
  """UARTConfig parity values."""
  NONE = 0
  ODD = 1
  EVEN = 2
  MARK = 3
  SPACE = 4
  
@unique
class FLOW_CONTROL(IntEnum):
  """UARTConfig flow control values."""
  DISABLED = 0
  ENABLED = 1
  
@unique
class DATA_BITS(IntEnum):
  """UARTConfig data bits values."""
  FIVE = 0
  SIX = 1
  SEVEN = 2
  EIGHT = 3


@unique
class STOP_BITS(IntEnum):
  """UARTConfig stop bits values."""
  SHORT = 0
  LONG = 1
  
class CP2110Device():
  
  last = 0
  fake_data = [
    [0x0B, 0x00, 0x83, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
    [0xde, 0xad, 0xbe, 0xef],
    [0x00, 0x0B, 0x00, 0x83, 0x01, 0x00],
    [0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
    [0x0D, 0x00, 0x84, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
  ]

  fake_index = 0

  def __init__(self, vid=None, pid=None, serial=None, path=None):
    print('Development: Using fake cp2110 library')
  
  def set_uart_config(self, config):
    pass
  
  def enable_uart(self):
    pass
  
  def read(self, size=None):
    now = time.time()
    if now - self.last > 1:
      self.last = now
      data = self.fake_data[self.fake_index]
      self.fake_index = self.fake_index + 1 if self.fake_index < len(self.fake_data) - 1 else 0
      return data
    else:
      return []


class UARTConfig:
  def __init__(self, baud, parity, flow_control, data_bits, stop_bits):
    pass
      
RX_TX_MAX = 63