import asyncio
import sys
from easylap import UnicastClient


async def main():
  client = UnicastClient(callback=lambda m: client.logger.info('Received: {}'.format(m)))
  # FIXME: Bad design: if create_endpoint is not called BEFORE browse_for_service, there will be no ping task
  # FIXME: We should not create an endpoint if there is no service
  if await client.create_endpoint(): 
    client.browse_for_service()
    await asyncio.sleep(2)
    if not client.remote_addr or not client.remote_port:
      print('Cannot find server, aborting.')
      sys.exit(1)
      
    count = 0
    while True:
      print("LIGHTS {}".format(count))
      await client.send('LIGHTS {}'.format(count << 2))
      count = count + 1
      if count >= (1 << 7):
        count = 0
      await asyncio.sleep(1)

if __name__ == '__main__':
  asyncio.run(main())
