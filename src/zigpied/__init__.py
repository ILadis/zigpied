
async def Controller(config):
    from zigpy_znp.zigbee.application import ControllerApplication
    return await ControllerApplication.new(config)

def NoopController():
    from zigpy.application import ControllerApplication

    async def noop(self, *args, **kwargs):
        pass

    methods = ControllerApplication.__dict__.copy()
    for method in ControllerApplication.__abstractmethods__:
        methods[method] = noop

    controller = type('NoopController', (ControllerApplication,), methods)
    config = { 'device': { 'path': '' } }

    return controller(config)

def Repository(path):
    from .repository import Repository
    return Repository.open(path)

def Observer(repository):
    from .observer import Observer
    return Observer(repository)

def Scanner():
    from .scanner import Scanner
    return Scanner()

def Server():
    from .server import Server
    return Server()
