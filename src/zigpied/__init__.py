
async def Controller(config):
    from zigpy_znp.zigbee.application import ControllerApplication
    return await ControllerApplication.new(config)

def Repository(path):
    from .repository import Repository
    return Repository.open(path)

def Observer(repository):
    from .observer import Observer
    return Observer(repository)

def Server():
    from .server import Server
    return Server()
