import requests
import random
import string
from urllib import parse
from io import BytesIO
from PIL import Image
from RtspClient import RtspClient


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

    def set_recording_encoding(self,
                               audio=0,
                               main_bit_rate=8192,
                               main_frame_rate=8,
                               main_profile='High',
                               main_size="2560*1440",
                               sub_bit_rate=160,
                               sub_frame_rate=7,
                               sub_profile='High',
                               sub_size='640*480') -> object:
        """
        Sets the current camera encoding settings for "Clear" and "Fluent" profiles.
        :param audio: int Audio on or off
        :param main_bit_rate: int Clear Bit Rate
        :param main_frame_rate: int Clear Frame Rate
        :param main_profile: string Clear Profile
        :param main_size: string Clear Size
        :param sub_bit_rate: int Fluent Bit Rate
        :param sub_frame_rate: int Fluent Frame Rate
        :param sub_profile: string Fluent Profile
        :param sub_size: string Fluent Size
        :return: response
        """
        body = [{"cmd": "SetEnc",
                 "action": 0,
                 "param":
                 {"Enc":
                  {"audio": audio,
                   "channel": 0,
                   "mainStream": {
                       "bitRate": main_bit_rate,
                       "frameRate": main_frame_rate,
                       "profile": main_profile,
                       "size": main_size},
                   "subStream": {
                       "bitRate": sub_bit_rate,
                       "frameRate": sub_frame_rate,
                       "profile": sub_profile,
                       "size": sub_size}}
                  }}]
        return self._execute_command('SetEnc', body)

    def set_advanced_imaging(self,
                             anti_flicker='Outdoor',
                             exposure='Auto',
                             gain_min=1,
                             gain_max=62,
                             shutter_min=1,
                             shutter_max=125,
                             blue_gain=128,
                             red_gain=128,
                             white_balance='Auto',
                             day_night='Auto',
                             back_light='DynamicRangeControl',
                             blc=128,
                             drc=128,
                             rotation=0,
                             mirroring=0,
                             nr3d=1) -> object:
        """
        Sets the advanced camera settings.
        :param anti_flicker: string
        :param exposure: string
        :param gain_min: int
        :param gain_max: string
        :param shutter_min: int
        :param shutter_max: int
        :param blue_gain: int
        :param red_gain: int
        :param white_balance: string
        :param day_night: string
        :param back_light: string
        :param blc: int
        :param drc: int
        :param rotation: int
        :param mirroring: int
        :param nr3d: int
        :return: response
        """
        body = [{
            "cmd": "SetIsp",
            "action": 0,
            "param": {
                "Isp": {
                    "channel": 0,
                    "antiFlicker": anti_flicker,
                    "exposure": exposure,
                    "gain": {"min": gain_min, "max": gain_max},
                    "shutter": {"min": shutter_min, "max": shutter_max},
                    "blueGain": blue_gain,
                    "redGain": red_gain,
                    "whiteBalance": white_balance,
                    "dayNight": day_night,
                    "backLight": back_light,
                    "blc": blc,
                    "drc": drc,
                    "rotation": rotation,
                    "mirroring": mirroring,
                    "nr3d": nr3d
                }
            }
        }]
        return self._execute_command('SetIsp', body)

    ###########
    # RTSP Stream
    ###########
    def open_video_stream(self, profile: str = "main", proxies=None) -> None:
        """
        'https://support.reolink.com/hc/en-us/articles/360007010473-How-to-Live-View-Reolink-Cameras-via-VLC-Media-Player'
        :param profile: profile is "main" or "sub"
        :param proxies: Default is none, example: {"host": "localhost", "port": 8000}
        """
        rtsp_client = RtspClient(
            ip=self.ip, username=self.username, password=self.password, proxies=proxies)
        rtsp_client.preview()

    def get_snap(self, timeout: int = 3, proxies=None) -> Image or None:
        """
        Gets a "snap" of the current camera video data and returns a Pillow Image or None
        :param timeout: Request timeout to camera in seconds
        :param proxies: http/https proxies to pass to the request object.
        :return: Image or None
        """
        data = {}
        data['cmd'] = 'Snap'
        data['channel'] = 0
        data['rs'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        data['user'] = self.username
        data['password'] = self.password
        parms = parse.urlencode(data).encode("utf-8")

        try:
            response = requests.get(self.url, proxies=proxies, params=parms, timeout=timeout)
            if response.status_code == 200:
                return Image.open(BytesIO(response.content))
            print("Could not retrieve data from camera successfully. Status:", response.stats_code)
            return None

        except Exception as e:
            print("Could not get Image data\n", e)
            raise
