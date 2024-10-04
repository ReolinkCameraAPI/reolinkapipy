from reolinkapi import Camera

import urllib3
import requests
from urllib3.util import create_urllib3_context

class CustomSSLContextHTTPAdapter(requests.adapters.HTTPAdapter):
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_context=self.ssl_context)

urllib3.disable_warnings()
ctx = create_urllib3_context()
ctx.load_default_certs()
ctx.set_ciphers("AES128-GCM-SHA256")
ctx.check_hostname = False

session = requests.session()
session.adapters.pop("https://", None)
session.mount("https://", CustomSSLContextHTTPAdapter(ctx))

## Add a custom http handler to add in different ciphers that may
## not be aloud by default in openssl which urlib uses
cam = Camera("url", "user", "password", https=True, session=session)
cam.reboot_camera()
