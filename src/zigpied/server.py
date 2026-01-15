
import logging

from aiohttp import web

class Server:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.app = web.Application()
        self.runner = None

    def register(self, method, path, handler, *context, stream=False):
        async def exchange(request):
            response = web.StreamResponse() if stream else web.Response()

            try:
                await handler(request, response, *context)
            except Exception as exception:
                if not stream or not response.prepared:
                    response.set_status(500)
                self.logger.error(exception, exc_info=True)

            return response

        route = web.RouteDef(method, path, exchange, dict())
        self.app.add_routes([route])

    async def start(self, host='localhost', port=8080):
        if self.runner is not None:
            return False

        runner = web.AppRunner(self.app)
        await runner.setup()

        site = web.TCPSite(runner, host, port)
        await site.start()

        self.runner = runner
        return True

    async def stop(self):
        if self.runner is None:
            return False

        await self.runner.cleanup()

        self.runner = None
        return True
