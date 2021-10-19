import logging
import sys
from os import path
from logging.handlers import SysLogHandler

class LogOptions:
  def __init__(self, log_level = logging.INFO, syslog = False, stdout = True):
    self.log_level = log_level
    self.syslog = syslog
    self.stdout = stdout
    
class Base:
 
  
  def __init__(self, name, log_options = LogOptions()):
    logger = logging.getLogger(name)
    logger.setLevel(log_options.log_level)
    handler = None
    if log_options.syslog:
      formatter = logging.Formatter('%(asctime)s %(message)s')
      if path.exists('/dev/log'):
        handler = SysLogHandler(address = '/dev/log')
      else:
        handler = logging.StreamHandler(sys.stderr)
      handler.setFormatter(formatter)
      logger.addHandler(handler)
      
    if log_options.stdout:
      handler = logging.StreamHandler(sys.stdout)
      handler.setFormatter(logging.Formatter('%(message)s'))
      logger.addHandler(handler)
 
    self.log_options = log_options     
    self.logger = logger
    
    
  def log(self, level, msg):
    self.logger.log(level, msg)
   
    
  def info(self, msg):
    self.logger.info(msg)
   
    
  def debug(self, msg):
    self.logger.debug(msg)
   
    
  def error(self, msg):
    self.logger.error(msg)