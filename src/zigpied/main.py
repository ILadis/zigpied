
import logging
import asyncio

import zigpied
from zigpied.handlers import permit_join, list_devices, query_metrics, stop

def run():
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

async def main():
    config = {
        'database_path': 'zigbee.db',
        'device': { 'path': '/dev/ttyUSB0' },
    }

    controller = await zigpied.Controller(config)
    repository = zigpied.Repository('metrics.db')

    observer = zigpied.Observer(repository)
    observer.observe(controller)

    future = asyncio.get_running_loop().create_future()

    server = zigpied.Server()
    server.register('POST', '/permit-join', permit_join, controller)
    server.register('GET', '/devices', list_devices, controller)
    server.register('GET', '/metrics', query_metrics, repository)
    server.register('POST', '/stop', stop, future)

    await server.start()

    try:
        await future
    except:
        pass

    await server.stop()
    await controller.shutdown()

if __name__ == '__main__':
    run()
