# Asynchronous reading from a EasyLap device.
 
import asyncio
import sys
from concurrent.futures._base import CancelledError

from .base import Base, LogOptions
from .device import EasyLapDeviceException
try:
  from cp2110 import CP2110Device, UARTConfig, PARITY, FLOW_CONTROL, DATA_BITS, STOP_BITS, RX_TX_MAX
except ImportError:
  try:
    from .fake.cp2110 import *
  except ImportError as e:
    print('Cannot import: {} - exiting.'.format(e))
    sys.exit(1)

  
class AioEasyLapDevice(Base):
  """ Asynchronous EasyLap device """
  
  EASYLAP_PID = 0x86B9
  KEY_TIME = "time"
  KEY_UID = "uid"
  
  def __init__(self, log_options = LogOptions()):
    """ Init, can throw exception """
    super().__init__('AioEasyLapDevice', log_options)
    
    try:
      self.device = CP2110Device(pid=self.EASYLAP_PID)
    
      self.device.set_uart_config(UARTConfig(
        baud=38400, parity=PARITY.NONE, flow_control=FLOW_CONTROL.DISABLED,
        data_bits=DATA_BITS.EIGHT, stop_bits=STOP_BITS.SHORT))
      self.device.enable_uart()
    except Exception as e:
      raise EasyLapDeviceException(e)
  
  
  async def receive(self):
    """ Async generator """
    try:
      d = self.device
      buf = []
      
      while True:
        chunk = d.read(RX_TX_MAX + 1)
        while chunk:
          buf += chunk
          await asyncio.sleep(0)
          chunk = d.read(RX_TX_MAX + 1)
      
        if not buf:
          await asyncio.sleep(0)
          continue
        
        if buf[0] == 0x0B: # Timer packet
          if len(buf) >= 3 and buf[2] != 0x83: # garbage? discard one
            buf = buf[1:]
          elif len(buf) >= 0x0B: # 11 bytes
            timer_value = (buf[3] | buf[4] << 8 | buf[5] << 16 | buf[6] << 32)
            # print("timer: %s" % timer_value)
            # yield({'t': timer_value, 'c': 0})
            yield({self.KEY_TIME: timer_value, self.KEY_UID: 0})
            buf = buf[0x0B + 1:]
             
        elif buf[0] == 0x0D: # Car packet
          if len(buf) >= 3 and buf[2] != 0x84: # garbage? discard one
            buf = buf[1:]
          elif len(buf) >= 0x0D: # 13 bytes
            uid = (buf[3] | buf[4] << 8)
            timer_value = (buf[7] | buf[8] << 8 | buf[9] << 16 | buf[10] << 32)
            # print("car: %s: %s" % (uid, timer_value))
            yield({self.KEY_TIME: timer_value, self.KEY_UID:uid})
            buf = buf[0x0D + 1:]
        
        else:  
          buf = buf[1:]
          
    except CancelledError as e:
      raise e
    except Exception as e:
      raise EasyLapDeviceException(e)
