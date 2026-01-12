
import sys
import logging
import asyncio

import zigpied
from zigpied.handlers import permit_join, list_devices, query_metrics, stop

def run():
    asyncio.run(main())

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s [%(levelname)9s] --- %(name)s: %(message)s')

    controller = await zigpied.Controller({
        'database_path': 'zigbee.db',
        'device': { 'path': '/dev/ttyUSB0' },
    })

    repository = zigpied.Repository('metrics.db')

    observer = zigpied.Observer(repository)
    observer.observe(controller)

    event = asyncio.Event()

    server = zigpied.Server()
    server.register('POST', '/permit-join', permit_join, controller)
    server.register('GET',  '/devices', list_devices, controller)
    server.register('GET',  '/metrics', query_metrics, repository)
    server.register('POST', '/stop', stop, event)

    await server.start(host='127.0.0.1', port=8089)

    try:
        await event.wait()
    except:
        pass

    await server.stop()
    await controller.shutdown()

if __name__ == '__main__':
    run()
