import io
import random
import string
from urllib import request

from PIL import Image

from RtspClient import RtspClient
from resthandle import Request


class RecordingAPIMixin:
    """API calls for recording/streaming image or video."""
    def get_recording_encoding(self) -> object:
        """
        Get the current camera encoding settings for "Clear" and "Fluent" profiles.
        See examples/response/GetEnc.json for example response data.
        :return: response json
        """
        body = [{"cmd": "GetEnc", "action": 1, "param": {"channel": 0}}]
        return self._execute_command('GetEnc', body)

    def get_recording_advanced(self) -> object:
        """
        Get recording advanced setup data
        See examples/response/GetRec.json for example response data.
        :return: response json
        """
        body = [{"cmd": "GetRec", "action": 1, "param": {"channel": 0}}]
        return self._execute_command('GetRec', body)

    ###########
    # RTSP Stream
    ###########
    def open_video_stream(self, profile: str = "main") -> Image:
        """
        profile is "main" or "sub"
        https://support.reolink.com/hc/en-us/articles/360007010473-How-to-Live-View-Reolink-Cameras-via-VLC-Media-Player
        :param profile:
        :return:
        """
        with RtspClient(ip=self.ip, username=self.username, password=self.password,
                        proxies={"host": "127.0.0.1", "port": 8000}) as rtsp_client:
            rtsp_client.preview()

    def get_snap(self, timeout: int = 3) -> Image or None:
        """
        Gets a "snap" of the current camera video data and returns a Pillow Image or None
        :param timeout: Request timeout to camera in seconds
        :return: Image or None
        """
        randomstr = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        snap = self.url + "?cmd=Snap&channel=0&rs=" \
               + randomstr \
               + "&user=" + self.username \
               + "&password=" + self.password
        try:
            req = request.Request(snap)
            req.set_proxy(Request.proxies, 'http')
            reader = request.urlopen(req, timeout)
            if reader.status == 200:
                b = bytearray(reader.read())
                return Image.open(io.BytesIO(b))
            print("Could not retrieve data from camera successfully. Status:", reader.status)
            return None

        except Exception as e:
            print("Could not get Image data\n", e)
            raise
