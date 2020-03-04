import io
import json
import random
import string
import sys
from urllib import request

import numpy
import rtsp
from PIL import Image

from RtspClient import RtspClient
from resthandle import Request


class APIHandler:
    """
    The APIHandler class is the backend part of the API.
    This handles communication directly with the camera.
    Current camera's tested: RLC-411WS

    All Code will try to follow the PEP 8 standard as described here: https://www.python.org/dev/peps/pep-0008/

    """

    def __init__(self, ip: str, username: str, password: str, https=False, **kwargs):
        """
        Initialise the Camera API Handler (maps api calls into python)
        :param ip:
        :param username:
        :param password:
        :param proxy: Add a proxy dict for requests to consume.
        eg: {"http":"socks5://[username]:[password]@[host]:[port], "https": ...}
        More information on proxies in requests: https://stackoverflow.com/a/15661226/9313679
        """
        scheme = 'https' if https else 'http'
        self.url = f"{scheme}://{ip}/cgi-bin/api.cgi"
        self.ip = ip
        self.token = None
        self.username = username
        self.password = password
        Request.proxies = kwargs.get("proxy")  # Defaults to None if key isn't found

    ###########
    # Token
    ###########

    def login(self) -> bool:
        """
        Get login token
        Must be called first, before any other operation can be performed
        :return: bool
        """
        try:
            body = [{"cmd": "Login", "action": 0,
                     "param": {"User": {"userName": self.username, "password": self.password}}}]
            param = {"cmd": "Login", "token": "null"}
            response = Request.post(self.url, data=body, params=param)
            if response is not None:
                data = response.json()[0]
                code = data["code"]
                if int(code) == 0:
                    self.token = data["value"]["Token"]["name"]
                    print("Login success")
                    return True
                print(self.token)
                return False
            else:
                print("Failed to login\nStatus Code:", response.status_code)
                return False
        except Exception as e:
            print("Error Login\n", e)
            raise
        
    def _execute_command(self, command, data, multi=False):
        """
        Send a POST request to the IP camera with given data.
        :param command: name of the command to send
        :param data: object to send to the camera (send as json)
        :param multi: whether the given command name should be added to the
        url parameters of the request. Defaults to False. (Some multi-step
        commands seem to not have a single command name)
        :return: response JSON as python object
        """
        params = {"token": self.token, 'cmd': command}
        if multi:
            del params['cmd']
        try:
            if self.token is None:
                raise ValueError("Login first")
            response = Request.post(self.url, data=data, params=params)
            return response.json()
        except Exception as e:
            print(f"Command {command} failed: {e}")
            raise

    ###########
    # NETWORK
    ###########

    ###########
    # SET Network
    ###########
    def set_net_port(self, http_port=80, https_port=443, media_port=9000, onvif_port=8000, rtmp_port=1935,
                     rtsp_port=554) -> bool:
        """
        Set network ports
        If nothing is specified, the default values will be used
        :param rtsp_port: int
        :param rtmp_port: int
        :param onvif_port: int
        :param media_port: int
        :param https_port: int
        :type http_port: int
        :return: bool
        """
        body = [{"cmd": "SetNetPort", "action": 0, "param": {"NetPort": {
            "httpPort": http_port,
            "httpsPort": https_port,
            "mediaPort": media_port,
            "onvifPort": onvif_port,
            "rtmpPort": rtmp_port,
            "rtspPort": rtsp_port
        }}}]
        self._execute_command('SetNetPort', body, multi=True)
        print("Successfully Set Network Ports")
        return True

    def set_wifi(self, ssid, password) -> json or None:
        body = [{"cmd": "SetWifi", "action": 0, "param": {
            "Wifi": {
                "ssid": ssid,
                "password": password
            }}}]
        return self._execute_command('SetWifi', body)

    ###########
    # GET
    ###########
    def get_net_ports(self) -> json or None:
        """
        Get network ports
        :return:
        """
        body = [{"cmd": "GetNetPort", "action": 1, "param": {}},
                {"cmd": "GetUpnp", "action": 0, "param": {}},
                {"cmd": "GetP2p", "action": 0, "param": {}}]
        return self._execute_command('GetNetPort', body, multi=True)

    def get_wifi(self):
        body = [{"cmd": "GetWifi", "action": 1, "param": {}}]
        return self._execute_command('GetWifi', body)

    def scan_wifi(self):
        body = [{"cmd": "ScanWifi", "action": 1, "param": {}}]
        return self._execute_command('ScanWifi', body)

    ###########
    # Display
    ###########

    ###########
    # GET
    ###########
    def get_osd(self) -> json or None:
        """
        Get OSD information.
        See examples/response/GetOsd.json for example response data.
        :return: json or None
        """
        body = [{"cmd": "GetOsd", "action": 1, "param": {"channel": 0}}]
        return self._execute_command('GetOsd', body)

    def get_mask(self) -> json or None:
        """
        Get the camera mask information.
        See examples/response/GetMask.json for example response data.
        :return: json or None
        """
        body = [{"cmd": "GetMask", "action": 1, "param": {"channel": 0}}]
        return self._execute_command('GetMask', body)

    ###########
    # SET
    ###########
    def set_osd(self, bg_color: bool = 0, channel: int = 0, osd_channel_enabled: bool = 0, osd_channel_name: str = "",
                osd_channel_pos: str = "Lower Right", osd_time_enabled: bool = 0,
                osd_time_pos: str = "Lower Right") -> bool:
        """
        Set OSD
        :param bg_color: bool
        :param channel: int channel id
        :param osd_channel_enabled: bool
        :param osd_channel_name: string channel name
        :param osd_channel_pos: string channel position ["Upper Left","Top Center","Upper Right","Lower Left","Bottom Center","Lower Right"]
        :param osd_time_enabled: bool
        :param osd_time_pos: string time position ["Upper Left","Top Center","Upper Right","Lower Left","Bottom Center","Lower Right"]
        :return:
        """
        body = [{"cmd": "SetOsd", "action": 1, "param": {
            "Osd": {"bgcolor": bg_color, "channel": channel,
                    "osdChannel": {"enable": osd_channel_enabled, "name": osd_channel_name,
                                   "pos": osd_channel_pos},
                    "osdTime": {"enable": osd_time_enabled, "pos": osd_time_pos}
                    }
        }}]
        r_data = self._execute_command('SetOsd', body)
        if r_data["value"]["rspCode"] == "200":
            return True
        print("Could not set OSD. Camera responded with status:", r_data["value"])
        return False

    ###########
    # SYSTEM
    ###########

    ###########
    # GET
    ###########
    def get_general_system(self) -> json or None:
        body = [{"cmd": "GetTime", "action": 1, "param": {}}, {"cmd": "GetNorm", "action": 1, "param": {}}]
        return self._execute_command('get_general_system', body, multi=True)

    def get_performance(self) -> json or None:
        """
        Get a snapshot of the current performance of the camera.
        See examples/response/GetPerformance.json for example response data.
        :return: json or None
        """
        body = [{"cmd": "GetPerformance", "action": 0, "param": {}}]
        return self._execute_command('GetPerformance', body)

    def get_information(self) -> json or None:
        """
        Get the camera information
        See examples/response/GetDevInfo.json for example response data.
        :return: json or None
        """
        body = [{"cmd": "GetDevInfo", "action": 0, "param": {}}]
        return self._execute_command('GetDevInfo', body)

    ###########
    # SET
    ###########
    def reboot_camera(self) -> bool:
        """
        Reboots the camera
        :return: bool
        """
        body = [{"cmd": "Reboot", "action": 0, "param": {}}]
        return self._execute_command('Reboot', body)

    ##########
    # User
    ##########

    ##########
    # GET
    ##########
    def get_online_user(self) -> json or None:
        """
        Return a list of current logged-in users in json format
        See examples/response/GetOnline.json for example response data.
        :return: json or None
        """
        body = [{"cmd": "GetOnline", "action": 1, "param": {}}]
        return self._execute_command('GetOnline', body)

    def get_users(self) -> json or None:
        """
        Return a list of user accounts from the camera in json format.
        See examples/response/GetUser.json for example response data.
        :return: json or None
        """
        body = [{"cmd": "GetUser", "action": 1, "param": {}}]
        return self._execute_command('GetUser', body)

    ##########
    # SET
    ##########
    def add_user(self, username: str, password: str, level: str = "guest") -> bool:
        """
        Add a new user account to the camera
        :param username: The user's username
        :param password: The user's password
        :param level: The privilege level 'guest' or 'admin'. Default is 'guest'
        :return: bool
        """
        body = [{"cmd": "AddUser", "action": 0,
                 "param": {"User": {"userName": username, "password": password, "level": level}}}]
        r_data = self._execute_command('AddUser', body)
        if r_data["value"]["rspCode"] == "200":
            return True
        print("Could not add user. Camera responded with:", r_data["value"])
        return False

    def modify_user(self, username: str, password: str) -> bool:
        """
        Modify the user's password by specifying their username
        :param username: The user which would want to be modified
        :param password: The new password
        :return: bool
        """
        body = [{"cmd": "ModifyUser", "action": 0, "param": {"User": {"userName": username, "password": password}}}]
        r_data = self._execute_command('ModifyUser', body)
        if r_data["value"]["rspCode"] == "200":
            return True
        print("Could not modify user:", username, "\nCamera responded with:", r_data["value"])
        return False

    def delete_user(self, username: str) -> bool:
        """
        Delete a user by specifying their username
        :param username: The user which would want to be deleted
        :return: bool
        """
        body = [{"cmd": "DelUser", "action": 0, "param": {"User": {"userName": username}}}]
        r_data = self._execute_command('DelUser', body)
        if r_data["value"]["rspCode"] == "200":
            return True
        print("Could not delete user:", username, "\nCamera responded with:", r_data["value"])
        return False

    ##########
    # Image Data
    ##########
    def get_snap(self, timeout: int = 3) -> Image or None:
        """
        Gets a "snap" of the current camera video data and returns a Pillow Image or None
        :param timeout: Request timeout to camera in seconds
        :return: Image or None
        """
        try:
            randomstr = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            snap = self.url + "?cmd=Snap&channel=0&rs=" \
                   + randomstr \
                   + "&user=" + self.username \
                   + "&password=" + self.password
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

    #########
    # Device
    #########
    def get_hdd_info(self) -> json or None:
        """
        Gets all HDD and SD card information from Camera
        See examples/response/GetHddInfo.json for example response data.
        :return: json or None
        """
        body = [{"cmd": "GetHddInfo", "action": 0, "param": {}}]
        return self._execute_command('GetHddInfo', body)

    def format_hdd(self, hdd_id: [int] = [0]) -> bool:
        """
        Format specified HDD/SD cards with their id's
        :param hdd_id: List of id's specified by the camera with get_hdd_info api. Default is 0 (SD card)
        :return: bool
        """
        body = [{"cmd": "Format", "action": 0, "param": {"HddInfo": {"id": hdd_id}}}]
        r_data = self._execute_command('Format', body)
        if r_data["value"]["rspCode"] == "200":
            return True
        print("Could not format HDD/SD. Camera responded with:", r_data["value"])
        return False

    ###########
    # Recording
    ###########

    ###########
    # SET
    ###########

    ###########
    # GET
    ###########
    def get_recording_encoding(self) -> json or None:
        """
        Get the current camera encoding settings for "Clear" and "Fluent" profiles.
        See examples/response/GetEnc.json for example response data.
        :return: json or None
        """
        body = [{"cmd": "GetEnc", "action": 1, "param": {"channel": 0}}]
        return self._execute_command('GetEnc', body)

    def get_recording_advanced(self) -> json or None:
        """
        Get recording advanced setup data
        See examples/response/GetRec.json for example response data.
        :return: json or None
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
        # with rtsp.Client(
        #         rtsp_server_uri="rtsp://"
        #                         + self.username + ":"
        #                         + self.password + "@"
        #                         + self.ip
        #                         + ":554//h264Preview_01_"
        #                         + profile) as client:
        #     return client
