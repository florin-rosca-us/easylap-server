# Fake adafruit_mcp230xx.mcp23017 module

class Fake_Pin:
  """ A fake pin """
  def __init__(self, i2c, index):
    self.i2c = i2c
    self.index = index
    self.value = False
    self.output = False
    
  def switch_to_output(self, value):
    self.output = value
  
    
class MCP23017:
  """ A fake MCP23017 device """
  
  pins = []
  
  def __init__(self, i2c):
    for i in range(0, 16):
      self.pins.append(Fake_Pin(i2c, i))
  
  
  def get_pin(self, index):
    return self.pins[index]