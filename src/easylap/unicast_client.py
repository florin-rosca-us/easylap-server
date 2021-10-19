# asyncio version of zeroconf from https://github.com/frawau/aiozeroconf
# From https://wiki.python.org/moin/UdpCommunication

import asyncio
import ipaddress
from aiozeroconf import ServiceBrowser, Zeroconf
from .base import LogOptions
from .unicast import Unicast


class UnicastClient(Unicast):
  """ Unicast client """
  
  service = None
  ip_addr = None # My IP
  port = None
  transport = None
  callback = None
  zeroconf = None
  browser = None
  ping_task = None
  
  remote_addr = None
  remove_port = None
  
  
  """ UDP client
  """
  def __init__(self, service='_easylap._udp.local.', port=5006, callback=None, log_options = LogOptions()):
    """
    :param service: the service name
    :param port: the local port
    :param callback: called when data is received 
    :param log_options: log options
    """
    super().__init__('UnicastClient', log_options)
    self.ip_addr = self.get_my_ip() # Call only once!!!
    self.service = service
    self.port = port
    self.callback = callback
    self.logger.info('Client starting...')


  async def create_endpoint(self):
    """ Create local endpoint """
    self.logger.debug('create_endpoint')
    ip_addr = self.ip_addr
    port = self.port
    self.logger.debug('Creating endpoint: {}:{}'.format(ip_addr, port))
    loop = asyncio.get_running_loop()
    try:
      transport, protocol = await loop.create_datagram_endpoint(lambda: self, local_addr=(ip_addr, port))
      return transport, protocol
    except Exception as e:
      self.logger.error('Cannot create endpoint: {}'.format(e))
      return None


  def connection_made(self, transport):
    """ Callback for create_datagram_endpoint """
    self.logger.debug('connection_made')
    self.transport = transport


  def datagram_received(self, data, addr):
    """ Callback for create_datagram_endpoint """
    self.logger.debug('datagram_received')
    message = data.decode()
    if self.callback:
      self.callback(message)
    self.logger.debug('Received %r from %s' % (message, addr))

    
  def connection_lost(self, exc):
    """ Callback for create_datagram_endpoint """
    self.logger.debug('connection_lost')
    self.logger.error('Connection lost: {}'.format(exc))
    self.cleanup()

    
  def error_received(self, err):
    """ Callback for create_datagram_endpoint """
    self.logger.debug('error_received')
    self.logger.error('Error: {}'.format(err))
    self.cleanup()


  def browse_for_service(self):
    self.logger.debug('browse_for_service')
    self.logger.info('Browsing for service...')
    loop = asyncio.get_event_loop()
    self.zeroconf = Zeroconf(loop)
    self.browser = ServiceBrowser(self.zeroconf, self.service, self)

          
  def add_service(self, zeroconf, type_, name):
    """ Callback for ServiceBrowser """
    self.logger.debug('add_service')
    asyncio.create_task(self.async_add_service(zeroconf, type_, name))


  async def async_add_service(self, zeroconf, type_, name):
    self.logger.debug('async_add_service')
    info = await zeroconf.get_service_info(type_, name)
    addr = str(ipaddress.ip_address(info.address))
    port = info.port
    self.logger.info('Remote endpoint: {}'.format((addr, port)))
    self.logger.debug("Remote service: {}".format(info))
    
    self.remote_addr = addr
    self.remote_port = port
    # FIXME: bad design, this should not be here:
    if self.transport:
      self.ping_task = asyncio.create_task(self.ping(self.transport, addr, port))


  async def ping(self, transport, addr, port):
    self.logger.debug('ping')
    while True:
      self.logger.debug('Pinging {} on port {}'.format(addr, port))
      transport.sendto(b'HELLO', (addr, port))
      await asyncio.sleep(10) # 10 seconds between pings
      
  async def send(self, message):
    self.logger.debug('send: {}'.format(message))
    if self.remote_addr and self.remote_port:
      self.transport.sendto(message.encode(), (self.remote_addr, self.remote_port))
    else:
      raise RuntimeError('Connection not established')
  
  
  def remove_service(self, zeroconf, type_, name):
    self.logger.debug('remove_service')
    self.logger.info("Service %s removed" % (name,))
    self.cleanup()

    
  def cleanup(self):
    self.logger.debug('cleanup')
    if self.ping_task:
      self.ping_task.cancel()
    if self.transport:
      self.transport.close()


  async def close(self): # TODO: do we need this?
    if self.zeroconf:
      await self.zeroconf.close()
