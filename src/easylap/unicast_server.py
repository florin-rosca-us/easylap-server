# See https://docs.python.org/3/library/asyncio-protocol.html#udp-echo-server
# See https://github.com/frawau/aiozeroconf
# See https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
# See https://en.wikipedia.org/wiki/Reserved_IP_addresses
# 
# Creates a UDP port and waits for clients to register with a 'HELLO' message then 
# sends data to all registered clients.
# This uses IPv4 only. It is possible to use IPv6 but if security extensions are present then
# this will have a hard time finding the correct IPv6 address. Make sure that the iOS client
# disables IPv6. See https://stackoverflow.com/questions/64102383/nwconnection-timeout 
#
# This can be stopped by sending SIGINT/SIGTERM. On Mac there is a mDNS cache service that will
# hold the service record even if this server stops. To flush the cache:
# See https://help.dreamhost.com/hc/en-us/articles/214981288-Flushing-your-DNS-cache-in-Mac-OS-X-and-Linux
# 
# Changes for running on Raspberry Pi
# Raspberry Pi comes with Python 3.7.3. We need a couple of changes:
# + import concurrent
# - except asyncio.exceptions.CancelledError: 
# + except concurrent.futures._base.CancelledError:
#
# Better idea: install Python 3.9 on Raspberry Pi?
# On Raspbery Pi the log info goes to /var/log/user.log 

import asyncio
import socket
import time
from aiozeroconf import ServiceInfo, Zeroconf

from .base import LogOptions
from .unicast import Unicast


class UnicastServer(Unicast):
  """ Unicast server """
  
  HELLO = 'HELLO'
  BYE = 'BYE'
  TIMEOUT = 15 # Remove client if not seen for this many seconds

  name = None
  version = None
  ip_addr = None
  service = None
  port = None
  transport = None
  clients = {} # Last seen in the form (ip_addr, port):time
  zeroconf = None
  
  
  def __init__(self, name = 'EasyLap Service', service='_easylap._udp.local.', version = '0.0.1', port=5005, log_options = LogOptions(), command_handler = None):
    """
    
    :param service: the service name
    :param version: the version
    :param port: the local port
    :param log_options: the log options
    :param command_handler: callback that receives messages from clients
    
    """
    super().__init__('UnicastServer', log_options)
    self.name = name
    self.ip_addr = self.get_my_ip() # Call only once!
    self.service = service
    self.version = version
    self.port = port
    self.command_handler = command_handler
    self.logger.info('Server starting...')
    
    
  async def register_service(self):
    self.logger.debug('register_service')
    name = self.name
    service = self.service
    ip_addr = self.ip_addr
    port = self.port
    version = self.version
    self.logger.info('Registering service: {} {}:{}'.format(service, ip_addr, port))
    fqdn = socket.gethostname()
    hostname = fqdn.split('.')[0]  
    desc = {'service': name, 'version': version}
    info = ServiceInfo(
            service,
            "{}.{}".format(name,  service),
            # addresses=[socket.inet_aton(ip_addr)],
            address = socket.inet_aton(ip_addr),
            port=port,
            properties=desc,
            server='{}.local.'.format(hostname))
    
    self.zeroconf = Zeroconf(asyncio.get_running_loop())
    await self.zeroconf.register_service(info)
    self.logger.debug('Service registered')


  async def create_endpoint(self):
    self.logger.debug('create_endpoint')
    ip_addr = '0.0.0.0'
    port = self.port
    self.logger.info('Creating endpoint: {}:{}'.format(ip_addr, port))
    loop = asyncio.get_running_loop()
    try: 
      transport, protocol = await loop.create_datagram_endpoint(lambda: self, local_addr=(ip_addr, port))
      self.logger.debug('Endpoint created')
      return transport, protocol
    except Exception as e:
      self.logger.error('Cannot create endpoint: {}'.format(e))
      return None


  def connection_made(self, transport):
    self.logger.debug('connection_made')
    """ Callback for create_datagram_endpoint """
    self.transport = transport

    
  def datagram_received(self, data, addr):
    self.logger.debug('datagram_received')
    """ Callback for create_datagram_endpoint """
    message = data.decode()
    self.logger.debug('Received %r from %s' % (message, addr))
    # Addr is a tuple (INET, PORT)
    if message == self.HELLO:
      if not addr in self.clients:
        self.logger.info('Adding client: {}'.format(addr)) 
      self.clients[addr] = int(time.time()) # Register client, update last seen (don't do it only once!)
    elif message == self.BYE:
      self.logger.info('Removing client: {}'.format(addr)) 
      self.clients.pop(addr) # Remove record
    elif self.command_handler: # Handle custom commands 
      try:
        self.command_handler(message)
      except Exception as e:
        self.logger.warning('Cannot handle command: {} - {}'.format(message, e))
      
    self.purge_clients()


  def purge_clients(self):
    self.logger.debug('purge_clients')
    now = int(time.time())
    for addr in [c for c in self.clients.keys()]: # Make an immutable copy of the keys list. Remember, addr = (IP, PORT)
      then = self.clients[addr]
      if now - then > self.TIMEOUT:
        self.logger.info('Removing client: {}'.format(addr)) 
        self.clients.pop(addr)

  
  async def send(self, data):
    self.logger.debug('send')
    self.logger.debug('send clients: {}'.format([c for c in self.clients.keys()]))
    if self.transport:
      for addr_port in self.clients.keys():
        self.transport.sendto(data, addr_port)
    self.purge_clients()

    
  async def close(self, *args):
    """ Closes the server as the result of a Unix signal. Do not use logging here. Logging in signal handlers can cause problems. """
    if self.zeroconf:
      await self.zeroconf.close()
