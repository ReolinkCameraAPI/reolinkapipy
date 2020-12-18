import requests
from typing import Dict, List, Optional, Union
from reolink_api.alarm import AlarmAPIMixin
from reolink_api.device import DeviceAPIMixin
from reolink_api.display import DisplayAPIMixin
from reolink_api.download import DownloadAPIMixin
from reolink_api.image import ImageAPIMixin
from reolink_api.motion import MotionAPIMixin
from reolink_api.network import NetworkAPIMixin
from reolink_api.ptz import PtzAPIMixin
from reolink_api.recording import RecordingAPIMixin
from reolink_api.resthandle import Request
from reolink_api.system import SystemAPIMixin
from reolink_api.user import UserAPIMixin
from reolink_api.zoom import ZoomAPIMixin


class APIHandler(AlarmAPIMixin,
                 DeviceAPIMixin,
                 DisplayAPIMixin,
                 DownloadAPIMixin,
                 ImageAPIMixin,
                 MotionAPIMixin,
                 NetworkAPIMixin,
                 PtzAPIMixin,
                 RecordingAPIMixin,
                 SystemAPIMixin,
                 UserAPIMixin,
                 ZoomAPIMixin):
    """
    The APIHandler class is the backend part of the API, the actual API calls
    are implemented in Mixins.
    This handles communication directly with the camera.
    Current camera's tested: RLC-411WS

    All Code will try to follow the PEP 8 standard as described here: https://www.python.org/dev/peps/pep-0008/
    """

    def __init__(self, ip: str, username: str, password: str, https: bool = False, **kwargs):
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
                # TODO: Verify this change w/ owner. Delete old code if acceptable.
                #  A this point, response is NoneType. There won't be a status code property.
                # print("Failed to login\nStatus Code:", response.status_code)
                print("Failed to login\nResponse was null.")
                return False
        except Exception as e:
            print("Error Login\n", e)
            raise

    def logout(self) -> bool:
        """
        Logout of the camera
        :return: bool
        """
        try:
            data = [{"cmd": "Logout", "action": 0}]
            self._execute_command('Logout', data)
            # print(ret)
            return True
        except Exception as e:
            print("Error Logout\n", e)
            return False

    def _execute_command(self, command: str, data: List[Dict], multi: bool = False) -> \
            Optional[Union[Dict, bool]]:
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
            if command == 'Download':
                # Special handling for downloading an mp4
                # Pop the filepath from data
                tgt_filepath = data[0].pop('filepath')
                # Apply the data to the params
                params.update(data[0])
                with requests.get(self.url, params=params, stream=True) as req:
                    if req.status_code == 200:
                        with open(tgt_filepath, 'wb') as f:
                            f.write(req.content)
                        return True
                    else:
                        print(f'Error received: {req.status_code}')
                        return False

            else:
                response = Request.post(self.url, data=data, params=params)
                return response.json()
        except Exception as e:
            print(f"Command {command} failed: {e}")
            raise
