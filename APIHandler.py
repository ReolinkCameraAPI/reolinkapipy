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

    def __init__(self, ip: str, username: str, password: str, https = False, **kwargs):
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
                data = json.loads(response.text)[0]
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
        try:
            if self.token is None:
                raise ValueError("Login first")

            body = [{"cmd": "SetNetPort", "action": 0, "param": {"NetPort": {
                "httpPort": http_port,
                "httpsPort": https_port,
                "mediaPort": media_port,
                "onvifPort": onvif_port,
                "rtmpPort": rtmp_port,
                "rtspPort": rtsp_port
            }}}]
            param = {"token": self.token}
            response = Request.post(self.url, data=body, params=param)
            if response is not None:
                if response.status_code == 200:
                    print("Successfully Set Network Ports")
                    return True
                else:
                    print("Something went wront\nStatus Code:", response.status_code)
                    return False
            return False
        except Exception as e:
            print("Setting Network Port Error\n", e)
            raise

    def set_wifi(self, ssid, password) -> json or None:
        try:
            if self.token is None:
                raise ValueError("Login first")
            body = [{"cmd": "SetWifi", "action": 0, "param": {
                "Wifi": {
                    "ssid": ssid,
                    "password": password
                }}}]
            param = {"cmd": "SetWifi", "token": self.token}
            response = Request.post(self.url, data=body, params=param)
            return json.loads(response.text)
        except Exception as e:
            print("Could not Set Wifi details", e)
            raise

    ###########
    # GET
    ###########
    def get_net_ports(self) -> json or None:
        """
        Get network ports
        :return:
        """
        try:
            if self.token is not None:
                raise ValueError("Login first")

            body = [{"cmd": "GetNetPort", "action": 1, "param": {}},
                    {"cmd": "GetUpnp", "action": 0, "param": {}},
                    {"cmd": "GetP2p", "action": 0, "param": {}}]
            param = {"token": self.token}
            response = Request.post(self.url, data=body, params=param)
            if response.status_code == 200:
                return json.loads(response.text)
            print("Could not get network ports data. Status:", response.status_code)
            return None
        except Exception as e:
            print("Get Network Ports", e)

    def get_link_local(self):
        """
        Get General network data
        This includes IP address, Device mac, Gateway and DNS
        :return:
        """
        try:
            if self.token is None:
                raise ValueError("Login first")

            body = [{"cmd": "GetLocalLink", "action": 1, "param": {}}]
            param = {"cmd": "GetLocalLink", "token": self.token}
            request = Request.post(self.url, data=body, params=param)
            if request.status_code == 200:
                return json.loads(request.text)
            print("Could not get ")
        except Exception as e:
            print("Could not get Link Local", e)
            raise

    def get_wifi(self):
        try:
            if self.token is None:
                raise ValueError("Login first")
            body = [{"cmd": "GetWifi", "action": 1, "param": {}}]
            param = {"cmd": "GetWifi", "token": self.token}
            response = Request.post(self.url, data=body, params=param)
            return json.loads(response.text)
        except Exception as e:
            print("Could not get Wifi\n", e)
            raise

    def scan_wifi(self):
        try:
            if self.token is None:
                raise ValueError("Login first")
            body = [{"cmd": "ScanWifi", "action": 1, "param": {}}]
            param = {"cmd": "ScanWifi", "token": self.token}
            response = Request.post(self.url, data=body, params=param)
            return json.loads(response.text)
        except Exception as e:
            print("Could not Scan wifi\n", e)
            raise

    ###########
    # Display
    ###########

    ###########
    # GET
    ###########
    def get_osd(self) -> json or None:
        """
        Get OSD information.
        Response data format is as follows:
        [{"cmd" : "GetOsd","code" : 0, "initial" : {
            "Osd" : {"bgcolor" : 0,"channel" : 0,"osdChannel" : {"enable" : 1,"name" : "Camera1","pos" : "Lower Right"},
            "osdTime" : {"enable" : 1,"pos" : "Top Center"}
            }},"range" : {"Osd" : {"bgcolor" : "boolean","channel" : 0,"osdChannel" : {"enable" : "boolean","name" : {"maxLen" : 31},
               "pos" : ["Upper Left","Top Center","Upper Right","Lower Left","Bottom Center","Lower Right"]
            },
            "osdTime" : {"enable" : "boolean","pos" : ["Upper Left","Top Center","Upper Right","Lower Left","Bottom Center","Lower Right"]
            }
         }},"value" : {"Osd" : {"bgcolor" : 0,"channel" : 0,"osdChannel" : {"enable" : 0,"name" : "FarRight","pos" : "Lower Right"},
            "osdTime" : {"enable" : 0,"pos" : "Top Center"}
         }}}]
        :return: json or None
        """
        try:
            param = {"cmd": "GetOsd", "token": self.token}
            body = [{"cmd": "GetOsd", "action": 1, "param": {"channel": 0}}]
            response = Request.post(self.url, data=body, params=param)
            if response.status_code == 200:
                return json.loads(response.text)
            print("Could not retrieve OSD from camera successfully. Status:", response.status_code)
            return None
        except Exception as e:
            print("Could not get OSD", e)
            raise

    def get_mask(self) -> json or None:
        """
        Get the camera mask information
        Response data format is as follows:
        [{"cmd" : "GetMask","code" : 0,"initial" : {
         "Mask" : {
            "area" : [{"block" : {"height" : 0,"width" : 0,"x" : 0,"y" : 0},"screen" : {"height" : 0,"width" : 0}}],
            "channel" : 0,
            "enable" : 0
            }
        },"range" : {"Mask" : {"channel" : 0,"enable" : "boolean","maxAreas" : 4}},"value" : {
         "Mask" : {
            "area" : null,
            "channel" : 0,
            "enable" : 0}
        }
        }]
        :return: json or None
        """
        try:
            param = {"cmd": "GetMask", "token": self.token}
            body = [{"cmd": "GetMask", "action": 1, "param": {"channel": 0}}]
            response = Request.post(self.url, data=body, params=param)
            if response.status_code == 200:
                return json.loads(response.text)
            print("Could not get Mask from camera successfully. Status:", response.status_code)
            return None
        except Exception as e:
            print("Could not get mask", e)
            raise

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
        try:
            param = {"cmd": "setOsd", "token": self.token}
            body = [{"cmd": "SetOsd", "action": 1, "param":
                {"Osd": {"bgcolor": bg_color, "channel": channel,
                         "osdChannel": {"enable": osd_channel_enabled, "name": osd_channel_name,
                                        "pos": osd_channel_pos},
                         "osdTime": {"enable": osd_time_enabled, "pos": osd_time_pos}
                         }
                 }
                     }]
            response = Request.post(self.url, data=body, params=param)
            if response.status_code == 200:
                r_data = json.loads(response.text)
                if r_data["value"]["rspCode"] == "200":
                    return True
                print("Could not set OSD. Camera responded with status:", r_data["value"])
                return False
            print("Could not set OSD. Status:", response.status_code)
            return False
        except Exception as e:
            print("Could not set OSD", e)
            raise

    ###########
    # SYSTEM
    ###########

    ###########
    # GET
    ###########
    def get_general_system(self) -> json or None:
        try:
            if self.token is None:
                raise ValueError("Login first")
            body = [{"cmd": "GetTime", "action": 1, "param": {}}, {"cmd": "GetNorm", "action": 1, "param": {}}]
            param = {"token": self.token}
            response = Request.post(self.url, data=body, params=param)
            if response.status_code == 200:
                return json.loads(response.text)
            print("Could not retrieve general information from camera successfully. Status:", response.status_code)
            return None
        except Exception as e:
            print("Could not get General System settings\n", e)
            raise

    def get_performance(self) -> json or None:
        """
        Get a snapshot of the current performance of the camera.
        Response data format is as follows:
        [{"cmd" : "GetPerformance",
        "code" : 0,
        "value" : {
        "Performance" : {
            "codecRate" : 2154,
            "cpuUsed" : 14,
            "netThroughput" : 0
            }
        }
        }]
        :return: json or None
        """
        try:
            param = {"cmd": "GetPerformance", "token": self.token}
            body = [{"cmd": "GetPerformance", "action": 0, "param": {}}]
            response = Request.post(self.url, data=body, params=param)
            if response.status_code == 200:
                return json.loads(response.text)
            print("Cound not retrieve performance information from camera successfully. Status:", response.status_code)
            return None
        except Exception as e:
            print("Could not get performance", e)
            raise

    def get_information(self) -> json or None:
        """
        Get the camera information
        Response data format is as follows:
        [{"cmd" : "GetDevInfo","code" : 0,"value" : {
         "DevInfo" : {
            "B485" : 0,
            "IOInputNum" : 0,
            "IOOutputNum" : 0,
            "audioNum" : 0,
            "buildDay" : "build 18081408",
            "cfgVer" : "v2.0.0.0",
            "channelNum" : 1,
            "detail" : "IPC_3816M100000000100000",
            "diskNum" : 1,
            "firmVer" : "v2.0.0.1389_18081408",
            "hardVer" : "IPC_3816M",
            "model" : "RLC-411WS",
            "name" : "Camera1_withpersonality",
            "serial" : "00000000000000",
            "type" : "IPC",
            "wifi" : 1
            }
        }
        }]
        :return: json or None
        """
        try:
            param = {"cmd": "GetDevInfo", "token": self.token}
            body = [{"cmd": "GetDevInfo", "action": 0, "param": {}}]
            response = Request.post(self.url, data=body, params=param)
            if response.status_code == 200:
                return json.loads(response.text)
            print("Could not retrieve camera information. Status:", response.status_code)
            return None
        except Exception as e:
            print("Could not get device information", e)
            raise

    ##########
    # User
    ##########

    ##########
    # GET
    ##########
    def get_online_user(self) -> json or None:
        """
        Return a list of current logged-in users in json format
        Response data format is as follows:
        [{"cmd" : "GetOnline","code" : 0,"value" : {
         "User" : [{
               "canbeDisconn" : 0,
               "ip" : "192.168.1.100",
               "level" : "admin",
               "sessionId" : 1000,
               "userName" : "admin"
               }]
            }
        }]
        :return: json or None
        """
        try:
            param = {"cmd": "GetOnline", "token": self.token}
            body = [{"cmd": "GetOnline", "action": 1, "param": {}}]
            response = Request.post(self.url, data=body, params=param)
            if response.status_code == 200:
                return json.loads(response.text)
            print("Could not retrieve online user from camera. Status:", response.status_code)
            return None
        except Exception as e:
            print("Could not get online user", e)
            raise

    def get_users(self) -> json or None:
        """
        Return a list of user accounts from the camera in json format
        Response data format is as follows:
        [{"cmd" : "GetUser","code" : 0,"initial" : {
         "User" : {
            "level" : "guest"
         }},
         "range" : {"User" : {
            "level" : [ "guest", "admin" ],
            "password" : {
               "maxLen" : 31,
               "minLen" : 6
            },
            "userName" : {
               "maxLen" : 31,
               "minLen" : 1
            }}
        },"value" : {
         "User" : [
            {
               "level" : "admin",
               "userName" : "admin"
            }]
        }
        }]
        :return: json or None
        """
        try:
            param = {"cmd": "GetUser", "token": self.token}
            body = [{"cmd": "GetUser", "action": 1, "param": {}}]
            response = Request.post(self.url, data=body, params=param)
            if response.status_code == 200:
                return json.loads(response.text)
            print("Could not retrieve users from camera. Status:", response.status_code)
            return None
        except Exception as e:
            print("Could not get users", e)
            raise

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
        try:
            param = {"cmd": "AddUser", "token": self.token}
            body = [{"cmd": "AddUser", "action": 0,
                     "param": {"User": {"userName": username, "password": password, "level": level}}}]
            response = Request.post(self.url, data=body, params=param)
            if response.status_code == 200:
                r_data = json.loads(response.text)
                if r_data["value"]["rspCode"] == "200":
                    return True
                print("Could not add user. Camera responded with:", r_data["value"])
                return False
            print("Something went wrong. Could not add user. Status:", response.status_code)
            return False
        except Exception as e:
            print("Could not add user", e)
            raise

    def modify_user(self, username: str, password: str) -> bool:
        """
        Modify the user's password by specifying their username
        :param username: The user which would want to be modified
        :param password: The new password
        :return: bool
        """
        try:
            param = {"cmd": "ModifyUser", "token": self.token}
            body = [{"cmd": "ModifyUser", "action": 0, "param": {"User": {"userName": username, "password": password}}}]
            response = Request.post(self.url, data=body, params=param)
            if response.status_code == 200:
                r_data = json.loads(response.text)
                if r_data["value"]["rspCode"] == "200":
                    return True
                print("Could not modify user:", username, "\nCamera responded with:", r_data["value"])
            print("Something went wrong. Could not modify user. Status:", response.status_code)
            return False
        except Exception as e:
            print("Could not modify user", e)
            raise

    def delete_user(self, username: str) -> bool:
        """
        Delete a user by specifying their username
        :param username: The user which would want to be deleted
        :return: bool
        """
        try:
            param = {"cmd": "DelUser", "token": self.token}
            body = [{"cmd": "DelUser", "action": 0, "param": {"User": {"userName": username}}}]
            response = Request.post(self.url, data=body, params=param)
            if response.status_code == 200:
                r_data = json.loads(response.text)
                if r_data["value"]["rspCode"] == "200":
                    return True
                print("Could not delete user:", username, "\nCamera responded with:", r_data["value"])
                return False
        except Exception as e:
            print("Could not delete user", e)
            raise

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
        Response data format is as follows:
        [{"cmd" : "GetHddInfo",
        "code" : 0,
        "value" : {
        "HddInfo" : [{
               "capacity" : 15181,
               "format" : 1,
               "id" : 0,
               "mount" : 1,
               "size" : 15181
                }]
            }
        }]

        :return: json or None
        """
        try:
            param = {"cmd": "GetHddInfo", "token": self.token}
            body = [{"cmd": "GetHddInfo", "action": 0, "param": {}}]
            response = Request.post(self.url, data=body, params=param)
            if response.status_code == 200:
                return json.loads(response.text)
            print("Could not retrieve HDD/SD info from camera successfully. Status:", response.status_code)
            return None
        except Exception as e:
            print("Could not get HDD/SD card information", e)
            raise

    def format_hdd(self, hdd_id: [int] = [0]) -> bool:
        """
        Format specified HDD/SD cards with their id's
        :param hdd_id: List of id's specified by the camera with get_hdd_info api. Default is 0 (SD card)
        :return: bool
        """
        try:
            param = {"cmd": "Format", "token": self.token}
            body = [{"cmd": "Format", "action": 0, "param": {"HddInfo": {"id": hdd_id}}}]
            response = Request.post(self.url, data=body, params=param)
            if response.status_code == 200:
                r_data = json.loads(response.text)
                if r_data["value"]["rspCode"] == "200":
                    return True
                print("Could not format HDD/SD. Camera responded with:", r_data["value"])
                return False
            print("Could not format HDD/SD. Status:", response.status_code)
            return False
        except Exception as e:
            print("Could not format HDD/SD", e)
            raise

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
        Response data format is as follows:
        [{
        "cmd" : "GetEnc",
        "code" : 0,
        "initial" : {
            "Enc" : {
                "audio" : 0,
                "channel" : 0,
                "mainStream" : {
                "bitRate" : 4096,
                "frameRate" : 15,
                "profile" : "High",
                "size" : "3072*1728"
                },
                "subStream" : {
                    "bitRate" : 160,
                    "frameRate" : 7,
                    "profile" : "High",
                    "size" : "640*360"
                }
            }
        },
        "range" : {
            "Enc" : [
                {
                "audio" : "boolean",
                "mainStream" : {
                    "bitRate" : [ 1024, 1536, 2048, 3072, 4096, 5120, 6144, 7168, 8192 ],
                    "default" : {
                        "bitRate" : 4096,
                        "frameRate" : 15
                    },
                    "frameRate" : [ 20, 18, 16, 15, 12, 10, 8, 6, 4, 2 ],
                    "profile" : [ "Base", "Main", "High" ],
                    "size" : "3072*1728"
                },
                "subStream" : {
                    "bitRate" : [ 64, 128, 160, 192, 256, 384, 512 ],
                    "default" : {
                        "bitRate" : 160,
                        "frameRate" : 7
                    },
                    "frameRate" : [ 15, 10, 7, 4 ],
                    "profile" : [ "Base", "Main", "High" ],
                    "size" : "640*360"
                    }
                },
                {
                "audio" : "boolean",
                "mainStream" : {
                    "bitRate" : [ 1024, 1536, 2048, 3072, 4096, 5120, 6144, 7168, 8192 ],
                    "default" : {
                        "bitRate" : 4096,
                        "frameRate" : 15
                    },
                    "frameRate" : [ 20, 18, 16, 15, 12, 10, 8, 6, 4, 2 ],
                    "profile" : [ "Base", "Main", "High" ],
                    "size" : "2592*1944"
                },
                "subStream" : {
                    "bitRate" : [ 64, 128, 160, 192, 256, 384, 512 ],
                    "default" : {
                        "bitRate" : 160,
                        "frameRate" : 7
                    },
                    "frameRate" : [ 15, 10, 7, 4 ],
                    "profile" : [ "Base", "Main", "High" ],
                    "size" : "640*360"
                }
            },
                {
                "audio" : "boolean",
                "mainStream" : {
                    "bitRate" : [ 1024, 1536, 2048, 3072, 4096, 5120, 6144, 7168, 8192 ],
                    "default" : {
                        "bitRate" : 3072,
                        "frameRate" : 15
                    },
                    "frameRate" : [ 30, 22, 20, 18, 16, 15, 12, 10, 8, 6, 4, 2 ],
                    "profile" : [ "Base", "Main", "High" ],
                    "size" : "2560*1440"
                },
                "subStream" : {
                    "bitRate" : [ 64, 128, 160, 192, 256, 384, 512 ],
                    "default" : {
                        "bitRate" : 160,
                        "frameRate" : 7
                    },
                    "frameRate" : [ 15, 10, 7, 4 ],
                    "profile" : [ "Base", "Main", "High" ],
                    "size" : "640*360"
                }
                },
                {
                "audio" : "boolean",
                "mainStream" : {
                    "bitRate" : [ 1024, 1536, 2048, 3072, 4096, 5120, 6144, 7168, 8192 ],
                    "default" : {
                        "bitRate" : 3072,
                        "frameRate" : 15
                    },
                    "frameRate" : [ 30, 22, 20, 18, 16, 15, 12, 10, 8, 6, 4, 2 ],
                    "profile" : [ "Base", "Main", "High" ],
                    "size" : "2048*1536"
                },
                "subStream" : {
                    "bitRate" : [ 64, 128, 160, 192, 256, 384, 512 ],
                    "default" : {
                        "bitRate" : 160,
                        "frameRate" : 7
                    },
                    "frameRate" : [ 15, 10, 7, 4 ],
                    "profile" : [ "Base", "Main", "High" ],
                    "size" : "640*360"
                }
                },
            {
                "audio" : "boolean",
                "mainStream" : {
                    "bitRate" : [ 1024, 1536, 2048, 3072, 4096, 5120, 6144, 7168, 8192 ],
                    "default" : {
                        "bitRate" : 3072,
                        "frameRate" : 15
                    },
                    "frameRate" : [ 30, 22, 20, 18, 16, 15, 12, 10, 8, 6, 4, 2 ],
                    "profile" : [ "Base", "Main", "High" ],
                    "size" : "2304*1296"
                },
                "subStream" : {
                    "bitRate" : [ 64, 128, 160, 192, 256, 384, 512 ],
                    "default" : {
                        "bitRate" : 160,
                        "frameRate" : 7
                    },
                    "frameRate" : [ 15, 10, 7, 4 ],
                    "profile" : [ "Base", "Main", "High" ],
                    "size" : "640*360"
                }
                }
            ]
        },
        "value" : {
            "Enc" : {
                "audio" : 0,
                "channel" : 0,
                "mainStream" : {
                "bitRate" : 2048,
                "frameRate" : 20,
                "profile" : "Main",
                "size" : "3072*1728"
                },
                "subStream" : {
                "bitRate" : 64,
                "frameRate" : 4,
                "profile" : "High",
                "size" : "640*360"
                }
            }
        }
        }]

        :return: json or None
        """
        try:
            param = {"cmd": "GetEnc", "token": self.token}
            body = [{"cmd": "GetEnc", "action": 1, "param": {"channel": 0}}]
            response = Request.post(self.url, data=body, params=param)
            if response.status_code == 200:
                return json.loads(response.text)
            print("Could not retrieve recording encoding data. Status:", response.status_code)
            return None
        except Exception as e:
            print("Could not get recording encoding", e)
            raise

    def get_recording_advanced(self) -> json or None:
        """
        Get recording advanced setup data
        Response data format is as follows:
        [{
        "cmd" : "GetRec",
        "code" : 0,
        "initial" : {
            "Rec" : {
                "channel" : 0,
                "overwrite" : 1,
                "postRec" : "15 Seconds",
                "preRec" : 1,
                "schedule" : {
                    "enable" : 1,
                    "table" : "111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111"
                }
            }
        },
        "range" : {
            "Rec" : {
                "channel" : 0,
                "overwrite" : "boolean",
                "postRec" : [ "15 Seconds", "30 Seconds", "1 Minute" ],
                "preRec" : "boolean",
                "schedule" : {
                    "enable" : "boolean"
                }
            }
        },
        "value" : {
            "Rec" : {
                "channel" : 0,
                "overwrite" : 1,
                "postRec" : "15 Seconds",
                "preRec" : 1,
                "schedule" : {
                    "enable" : 1,
                    "table" : "000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
                }
            }
        }
        }]

        :return: json or None
        """
        try:
            param = {"cmd": "GetRec", "token": self.token}
            body = [{"cmd": "GetRec", "action": 1, "param": {"channel": 0}}]
            response = Request.post(self.url, data=body, params=param)
            if response.status_code == 200:
                return json.loads(response.text)
            print("Could not retrieve advanced recording. Status:", response.status_code)
            return None
        except Exception as e:
            print("Could not get advanced recoding", e)

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
