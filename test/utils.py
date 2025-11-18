
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
