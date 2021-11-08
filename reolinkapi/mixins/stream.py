import string
from random import choices
from typing import Any, Optional
from urllib import parse
from io import BytesIO

import requests

try:
    from PIL.Image import Image, open as open_image

    from reolinkapi.utils.rtsp_client import RtspClient


    class StreamAPIMixin:
        """ API calls for opening a video stream or capturing an image from the camera."""

        def open_video_stream(self, callback: Any = None, proxies: Any = None) -> Any:
            """
            'https://support.reolink.com/hc/en-us/articles/360007010473-How-to-Live-View-Reolink-Cameras-via-VLC-Media-Player'
            Blocking function creates a generator and returns the frames as it is spawned
            :param callback:
            :param proxies: Default is none, example: {"host": "localhost", "port": 8000}
            """
            rtsp_client = RtspClient(
                ip=self.ip, username=self.username, password=self.password, profile=self.profile, proxies=proxies, callback=callback)
            return rtsp_client.open_stream()

        def get_snap(self, timeout: float = 3, proxies: Any = None) -> Optional[Image]:
            """
            Gets a "snap" of the current camera video data and returns a Pillow Image or None
            :param timeout: Request timeout to camera in seconds
            :param proxies: http/https proxies to pass to the request object.
            :return: Image or None
            """
            data = {
                'cmd': 'Snap',
                'channel': 0,
                'rs': ''.join(choices(string.ascii_uppercase + string.digits, k=10)),
                'user': self.username,
                'password': self.password,
            }
            parms = parse.urlencode(data).encode("utf-8")

            try:
                response = requests.get(self.url, proxies=proxies, params=parms, timeout=timeout)
                if response.status_code == 200:
                    return open_image(BytesIO(response.content))
                print("Could not retrieve data from camera successfully. Status:", response.status_code)
                return None

            except Exception as e:
                print("Could not get Image data\n", e)
                raise
except ImportError:
    class StreamAPIMixin:
        """ API calls for opening a video stream or capturing an image from the camera."""

        def open_video_stream(self, callback: Any = None, proxies: Any = None) -> Any:
            raise ImportError('''open_video_stream requires streaming extra dependencies\nFor instance "pip install reolinkapi[streaming]"''')

        def get_snap(self, timeout: float = 3, proxies: Any = None) -> Optional['Image']:
            raise ImportError('''open_video_stream requires streaming extra dependencies\nFor instance "pip install reolinkapi[streaming]"''')
