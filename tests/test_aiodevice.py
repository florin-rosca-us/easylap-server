import asyncio
from easylap import AioEasyLapDevice

async def main():
  easylap = AioEasyLapDevice()
  async for m in easylap.receive():
    print(m)
  
if __name__ == '__main__':
  asyncio.run(main())
  