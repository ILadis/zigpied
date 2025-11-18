
async def permit_join(request, response, controller):
    await controller.permit(60)
    response.set_status(200)

async def list_devices(request, response, controller):
    from json import dumps
    from datetime import datetime

    devices = []
    for device in controller.devices.values():
        devices.append({
            'id':           int(device.manufacturer_id),
            'address':      str(device.ieee),
            'model':        str(device.model),
            'manufacturer': str(device.manufacturer),
            'last_seen': datetime.fromtimestamp(device.last_seen).strftime('%Y-%m-%dT%H:%M:%S'),
        })

    response.set_status(200)
    response.content_type = 'application/json'
    response.text = dumps(devices)

async def query_metrics(request, response, repository):
    from json import dumps
    from datetime import datetime

    address = request.rel_url.query.get('address', None)
    metric  = request.rel_url.query.get('metric',  None)
    after   = request.rel_url.query.get('after',   None)
    before  = request.rel_url.query.get('before',  None)

    try:
        if after:  after  = datetime.strptime(after,  '%Y-%m-%dT%H:%M:%S').timestamp()
        if before: before = datetime.strptime(before, '%Y-%m-%dT%H:%M:%S').timestamp()
    except:
        response.set_status(400)
        return

    metrics = []
    for log in repository.query(address, metric, after, before):
        metrics.append({
            'address': str(log.address),
            'metric':  str(log.metric),
            'value':   float(log.value),
            'timestamp': datetime.fromtimestamp(log.timestamp).strftime('%Y-%m-%dT%H:%M:%S'),
        })

    response.set_status(200)
    response.content_type = 'application/json'
    response.text = dumps(metrics)

async def stop(request, response, future):
    future.cancel()
    response.set_status(200)
