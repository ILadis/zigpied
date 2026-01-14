
import logging

from bleak import BleakScanner

class Scanner:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.handlers = list()
        self.scanner = None

    def register(self, handler, *context):
        def callback(device, adv_data):
            try:
                handler(device, adv_data, *context)
            except Exception as exception:
                self.logger.error(exception, exc_info=True)

        self.handlers.append(callback)

    async def start(self):
        if self.scanner is not None:
            return False

        def discovered(device, advertising):
            for handler in self.handlers:
                handler(device, advertising)

        scanner = BleakScanner(discovered)
        await scanner.start()

        self.scanner = scanner
        return True

    async def stop(self):
        if self.scanner is None:
            return False

        await self.scanner.stop()
        self.scanner = None

        return True
