import json

from resthandle import Request


class APIHandler:

    def __init__(self, ip, https=False):
        scheme = 'https' if https else 'http'
        self.url = f"{scheme}://{ip}/cgi-bin/api.cgi"
        self.token = None

    # Token

    def login(self, username: str, password: str):
        """
        Get login token
        Must be called first, before any other operation can be performed
        :param username:
        :param password:
        :return:
        """
        try:
            body = [{"cmd": "Login", "action": 0, "param": {"User": {"userName": username, "password": password}}}]
            param = {"cmd": "Login", "token": "null"}
            response = Request.post(self.url, data=body, params=param)
            if response is not None:
                data = json.loads(response.text)[0]
                code = data["code"]
                if int(code) == 0:
                    self.token = data["value"]["Token"]["name"]
                    print("Login success")
                print(self.token)
            else:
                print("Failed to login\nStatus Code:", response.status_code)
        except Exception as e:
            print("Error Login\n", e)
            raise

    ###########
    # NETWORK
    ###########

    ###########
    # SET Network
    ###########
    def set_net_port(self, httpPort=80, httpsPort=443, mediaPort=9000, onvifPort=8000, rtmpPort=1935, rtspPort=554):
        """
        Set network ports
        If nothing is specified, the default values will be used
        :param httpPort:
        :param httpsPort:
        :param mediaPort:
        :param onvifPort:
        :param rtmpPort:
        :param rtspPort:
        :return:
        """
        try:
            if self.token is None:
                raise ValueError("Login first")

            body = [{"cmd": "SetNetPort", "action": 0, "param": {"NetPort": {
                "httpPort": httpPort,
                "httpsPort": httpsPort,
                "mediaPort": mediaPort,
                "onvifPort": onvifPort,
                "rtmpPort": rtmpPort,
                "rtspPort": rtspPort
            }}}]
            param = {"token": self.token}
            response = Request.post(self.url, data=body, params=param)
            if response is not None:
                if response.status_code == 200:
                    print("Successfully Set Network Ports")
                else:
                    print("Something went wront\nStatus Code:", response.status_code)

        except Exception as e:
            print("Setting Network Port Error\n", e)
            raise

    def set_wifi(self, ssid, password):
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
    def get_general_system(self):
        try:
            if self.token is None:
                raise ValueError("Login first")
            body = [{"cmd": "GetTime", "action": 1, "param": {}}, {"cmd": "GetNorm", "action": 1, "param": {}}]
            param = {"token": self.token}
            response = Request.post(self.url, data=body, params=param)
            return json.loads(response.text)
        except Exception as e:
            print("Could not get General System settings\n", e)
            raise
