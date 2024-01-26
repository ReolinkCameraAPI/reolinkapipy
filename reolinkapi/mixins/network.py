from typing import Dict


class NetworkAPIMixin:
    """API calls for network settings."""
    def set_net_port(self, http_enable: bool = False, http_port: float = 80,
                     https_enable: bool = True, https_port: float = 443, media_port: float = 9000,
                     onvif_enable: bool = True, onvif_port: float = 8000,
                     rtmp_enable: bool = False, rtmp_port: float = 1935, rtsp_enable: bool = True, rtsp_port: float = 554) -> bool:
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
        if http_enable:
            http_enable = 1
        else:
            http_enable = 0
        if https_enable:
            https_enable = 1
        else:
            https_enable = 0
        if onvif_enable:
            onvif_enable = 1
        else:
            onvif_enable = 0
        if rtmp_enable:
            rtmp_enable = 1
        else:
            rtmp_enable = 0
        if rtsp_enable:
            rtsp_enable = 1
        else:
            rtsp_enable = 0

        body = [{"cmd": "SetNetPort", "action": 0, "param": {"NetPort": {
            "httpEnable": http_enable,
            "httpPort": http_port,
            "httpsEnable": https_enable,
            "httpsPort": https_port,
            "mediaPort": media_port,
            "onvifEnable": onvif_enable,
            "onvifPort": onvif_port,
            "rtmpEnable": rtmp_enable,
            "rtmpPort": rtmp_port,
            "rtspEnable": rtsp_enable,
            "rtspPort": rtsp_port
        }}}]
        response = self._execute_command('SetNetPort', body, multi=True)
        if response[0]["code"] == 0:
            print("Successfully Set Network Ports")
            return True
        else:
            raise Exception(f"Failure to set network ports: {response}")

    def set_wifi(self, ssid: str, password: str) -> Dict:
        body = [{"cmd": "SetWifi", "action": 0, "param": {
            "Wifi": {
                "ssid": ssid,
                "password": password
            }}}]
        return self._execute_command('SetWifi', body)

    def get_net_ports(self) -> Dict:
        """
        Get network ports
        See examples/response/GetNetworkAdvanced.json for example response data.
        :return: response json
        """
        body = [{"cmd": "GetNetPort", "action": 1, "param": {}},
                {"cmd": "GetUpnp", "action": 0, "param": {}},
                {"cmd": "GetP2p", "action": 0, "param": {}}]
        return self._execute_command('GetNetPort', body, multi=True)

    def get_wifi(self) -> Dict:
        body = [{"cmd": "GetWifi", "action": 1, "param": {}}]
        return self._execute_command('GetWifi', body)

    def scan_wifi(self) -> Dict:
        body = [{"cmd": "ScanWifi", "action": 1, "param": {}}]
        return self._execute_command('ScanWifi', body)

    def get_network_general(self) -> Dict:
        """
        Get the camera information
        See examples/response/GetNetworkGeneral.json for example response data.
        :return: response json
        """
        body = [{"cmd": "GetLocalLink", "action": 0, "param": {}}]
        return self._execute_command('GetLocalLink', body)

    def get_network_ddns(self) -> Dict:
        """
        Get the camera DDNS network information
        See examples/response/GetNetworkDDNS.json for example response data.
        :return: response json
        """
        body = [{"cmd": "GetDdns", "action": 0, "param": {}}]
        return self._execute_command('GetDdns', body)

    def get_network_ntp(self) -> Dict:
        """
        Get the camera NTP network information
        See examples/response/GetNetworkNTP.json for example response data.
        :return: response json
        """
        body = [{"cmd": "GetNtp", "action": 0, "param": {}}]
        return self._execute_command('GetNtp', body)

    def get_network_email(self) -> Dict:
        """
        Get the camera email network information
        See examples/response/GetNetworkEmail.json for example response data.
        :return: response json
        """
        body = [{"cmd": "GetEmail", "action": 0, "param": {}}]
        return self._execute_command('GetEmail', body)

    def get_network_ftp(self) -> Dict:
        """
        Get the camera FTP network information
        See examples/response/GetNetworkFtp.json for example response data.
        :return: response json
        """
        body = [{"cmd": "GetFtp", "action": 0, "param": {}}]
        return self._execute_command('GetFtp', body)

    def get_network_push(self) -> Dict:
        """
        Get the camera push network information
        See examples/response/GetNetworkPush.json for example response data.
        :return: response json
        """
        body = [{"cmd": "GetPush", "action": 0, "param": {}}]
        return self._execute_command('GetPush', body)

    def get_network_status(self) -> Dict:
        """
        Get the camera status network information
        See examples/response/GetNetworkGeneral.json for example response data.
        :return: response json
        """
        return self.get_network_general()
