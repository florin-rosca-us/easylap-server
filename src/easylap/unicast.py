import socket
from .base import Base, LogOptions


class Unicast(Base):
  """ Base class for unicast client and server """

  
  def __init__(self, name, log_options = LogOptions()):
    super().__init__(name, log_options)
    
    
  def get_my_ip(self):
    """ Returns the IPv4 address. """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't even have to be reachable
        # Used for local communications within a private network.
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip
  
  
  def get_my_ip6(self):
    """ Returns the IPv6 address. Not reliable: returns a temporary address. """
    s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    try:
        # Doesn't even have to be reachable
        # Addresses used in documentation and example source code
        s.connect(('2001:db8::', 1)) 
        # Bummer: since this is "outgoing", the socket will be bound to a temporary address
        ip = s.getsockname()[0]
    except Exception:
        ip = '::1'
    finally:
        s.close()
    return ip