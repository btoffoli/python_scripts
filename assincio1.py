import asyncio

def hello():
    print('Hello lalala')

loop = asyncio.get_event_loop()
loop.call_soon(hello)
loop.run_forever()