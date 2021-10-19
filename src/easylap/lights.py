import sys
from .base import Base

# Lights on and off.

try:
  # These are available only on Raspberry Pi
  import board
  import busio
  import digitalio
  from adafruit_mcp230xx.mcp23017 import MCP23017
except:
  # For development on Mac
  try:
    import easylap.fake.board as board
    import easylap.fake.busio as busio
    import easylap.fake.digitalio as digitalio
    from .fake.mcp23017 import MCP23017
  except ImportError as e:
    print('Cannot import: {} - exiting.'.format(e))
    sys.exit(1)
    
    
class Lights(Base):
  
  pins = []
  
  def __init__(self, log_options):
    super().__init__('Lights', log_options)
    i2c = busio.I2C(board.SCL, board.SDA)
    mcp = MCP23017(i2c)  # MCP23017

    for i in range(0, 16):
      pin = mcp.get_pin(i)
      pin.switch_to_output(value=True)
      self.pins.append(pin)

    
  def set(self, value):
    """ 
    Turns LEDs on or off. Do not use logging here: can be called after a signal was received.
    
    :param value: bit-encoded     
    """
    if value < 0 or value > 0xFFFF:
      raise RuntimeError('Value out of range')
    for i in range(0, 16):
      self.pins[i].value = value & (1<<i)
      
      
  def on(self):
    """ All lights on """
    self.set(0xFFFF)
    
    
  def off(self):
    """ All lights off """
    self.set(0)
