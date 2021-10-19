import asyncio
import os
import concurrent.futures # Python 3.7 only
from easylap import UnicastServer
from signal import SIGINT, SIGTERM

async def main():
  server = UnicastServer()
  if await server.create_endpoint():
    await server.register_service()
    while True:
      # TODO: send data from a source
      try:
        await server.send(b'WHAT?')
        await asyncio.sleep(0.5)
      # except asyncio.exceptions.CancelledError:
      except concurrent.futures._base.CancelledError:
        await server.close()
        break
  
if __name__ == '__main__':
  print('zeroconf_unicast_server')
  print('pid={}'.format(os.getpid()))
  main_task = asyncio.ensure_future(main())
  loop = asyncio.get_event_loop()
  for signal in [SIGINT, SIGTERM]:
        loop.add_signal_handler(signal, main_task.cancel)
  loop.run_until_complete(main_task)