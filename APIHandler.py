import io
import json
import random
import string
from urllib.request import urlopen

from PIL import Image

from resthandle import Request


class APIHandler:
    """
    The APIHandler class is the backend part of the API.
    This handles communication directly with the camera.

    All Code will try to follow the PEP 8 standard as described here: https://www.python.org/dev/peps/pep-0008/

    """

    def __init__(self, ip: str, username: str, password: str):
        """
        Initialise the Camera API Handler (maps api calls into python)
        :param ip:
        :param username:
        :param password:
        """
        self.url = "http://" + ip + "/cgi-bin/api.cgi"
        self.token = None
        self.username = username
        self.password = password

    # Token

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
    def get_net_ports(self):
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
            return json.loads(response.text)
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
            return json.loads(request.text)
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

    def get_osd(self) -> json or None:
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

    ##########
    # User
    ##########

    ##########
    # GET
    ##########
    def get_online_user(self) -> json or None:
        """
        Return a list of current logged-in users in json format
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
            snap = "?cmd=Snap&channel=0&rs=" \
                   + randomstr \
                   + "&user=" + self.username \
                   + "&password=" + self.password
            reader = urlopen(self.url + snap, timeout)
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
        Format is as follows:
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
