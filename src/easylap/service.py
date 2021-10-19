
import argparse
import asyncio
import logging
import json
import sys
import traceback

from concurrent.futures._base import CancelledError
from signal import SIGHUP, SIGINT, SIGTERM

from .aiodevice import AioEasyLapDevice
from .base import Base, LogOptions
from .device import EasyLapDeviceException
from .lights import Lights
from .unicast_server import UnicastServer


class CreateService(Base):
  
  LIGHTS = 'LIGHTS'

  
  def __init__(self, args):
    
    parser = argparse.ArgumentParser(description='EasyLap service')
    parser.add_argument('-d', '--daemon', help='run as daemon', required=False, default=False, action='store_true')
    parser.add_argument('-v', '--verbose', help='show detailed info', required=False, default=False, action='store_true')
    parsed_args = parser.parse_args(args)
    log_options = LogOptions()
    if parsed_args.daemon:
      log_options.syslog = True
      log_options.stdout = False
    else:
      log_options.syslog = False
      log_options.stdout = True
    if parsed_args.verbose:
      log_options.log_level = logging.DEBUG
    
    super().__init__('CreateService', log_options)
    main_task = asyncio.ensure_future(self.main())
    loop = asyncio.get_event_loop()
    # for signal in [SIGINT, SIGTERM]:
    #       loop.add_signal_handler(signal, main_task.cancel)
    
    signals = (SIGHUP, SIGTERM, SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(self.shutdown(s, loop)))
    
    try:
      loop.run_until_complete(main_task)  
    except CancelledError:
      self.info('Done')


  async def shutdown(self, signal, loop):
    """Cleanup tasks tied to the service's shutdown."""
    logging.info(f"Received exit signal {signal.name}...")
    logging.info("Shutting down...")
    tasks = [t for t in asyncio.all_tasks() if t is not
             asyncio.current_task()]
    [task.cancel() for task in tasks]
    logging.info(f"Cancelling {len(tasks)} outstanding tasks")
    await asyncio.gather(*tasks)
    loop.stop()


  def handle_message(self, lights, message):
    """ Cannot be async because it is called from a callback in server. Should be handled quickly or should create an asynchronous task. """
    if message.startswith(self.LIGHTS):
      value = message[len(self.LIGHTS):].strip()
      if value == 'ON':
        lights.on()
      elif value == 'OFF':
        lights.off()
      else:
        lights.set(int(value))
  
  
  async def main(self):
    self.debug("main")
    
    lights = None
    
    try:
      lights = Lights(log_options = self.log_options)
      lights.on() # Started
      server = UnicastServer(log_options=self.log_options, command_handler = lambda message: self.handle_message(lights, message))
     
      if not await server.create_endpoint():
        self.logger.error('Could not create endpoint, exiting')
        sys.exit(1)
      await server.register_service()
      
      await asyncio.sleep(1)
      lights.set((1<<3)+(1<<5)) # Waiting. On the 5 lights bar the first light start at pin=2 !!!
  
      while True: # Do not let a EasyLapDeviceException stop this service
        try:
          await asyncio.sleep(1)
          easylap = AioEasyLapDevice(log_options=self.log_options) # May not be connected
          async for packet in easylap.receive():
            await server.send(json.dumps(packet).encode())
            await asyncio.sleep(0)      
        except EasyLapDeviceException as e:
          self.logger.debug('Device error: {}'.format(e.wrapped))

    except CancelledError:
      pass
    except Exception as e:
      self.error(traceback.format_exc())
    finally:
      try:
        lights.off()
        await server.close()
      finally:
        sys.exit(0)     
