from typing import Dict


class NetworkAPIMixin:
    """API calls for network settings."""
    def set_net_port(self, http_port: float = 80, https_port: float = 443, media_port: float = 9000,
                     onvif_port: float = 8000, rtmp_port: float = 1935, rtsp_port: float = 554) -> bool:
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
