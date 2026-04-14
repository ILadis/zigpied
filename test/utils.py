
import asyncio
import urllib

def fetch(method, url, data='', headers={}):
    request = urllib.request.Request(url, data.encode('utf-8'), method=method, headers=headers)

    def execute():
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.HTTPError as error:
            response = error
        return response

    loop = asyncio.get_running_loop()
    return loop.run_in_executor(None, execute)

def noop_controller(config):
    from zigpy.application import ControllerApplication
    from zigpy.zdo.types import NodeDescriptor

    async def noop(self, *args, **kwargs):
        pass

    methods = ControllerApplication.__dict__.copy()
    for method in ControllerApplication.__abstractmethods__:
        methods[method] = noop

    controller = type('NoopController', (ControllerApplication,), methods)
    app = controller(config)

    device = app.add_device(
        app.state.node_info.ieee,
        app.state.node_info.nwk)

    device.node_desc = NodeDescriptor()
    device.add_endpoint(0x1)
 
    return app

def add_device(app, ieee, nwk):
    import zigpy.types as types
    from zigpy.zdo.types import NodeDescriptor
    from zigpy.endpoint import Status

    ieee = types.EUI64.convert(ieee)
    nwk = types.NWK.convert(nwk)

    device = app.add_device(ieee, nwk)
    device.node_desc = NodeDescriptor

    endpoint = device.add_endpoint(0x1)
    endpoint.profile_id = 260
    endpoint.status = Status.ZDO_INIT

    address = types.AddrModeAddress(addr_mode=types.AddrMode.NWK, address=nwk)

    return endpoint, address
