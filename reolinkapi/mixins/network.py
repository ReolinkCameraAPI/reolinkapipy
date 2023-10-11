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
        # print("Successfully Set Network Ports")
        return True

    def set_network_ftp(self, username, password, directory, server_ip, enable) -> Dict:
        """
        Set the camera FTP network information
        {
            "cmd": "GetFtp",
            "code": 0,
            "value": {
                "Ftp": {
                    "anonymous": 0,
                    "interval": 15,
                    "maxSize": 100,
                    "mode": 0,
                    "password": "***********",
                    "port": 21,
                    "remoteDir": "incoming1",
                    "schedule": {
                        "enable": 1,
                        "table": "111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111"
                    },
                    "server": "192.168.1.2",
                    "streamType": 0,
                    "userName": "ftpuser"
                }
            }
        }
        
        For Version 2.0 API:
        [{
            "cmd": "SetFtpV20", "param": {
                "Ftp": { "anonymous": 0,
                    "autoDir": 1,
                    "bpicSingle": 0, "bvideoSingle": 0,
                    "enable": 1,
                    "interval": 30,
                    "maxSize": 100,
                    "mode": 0,
                    "onlyFtps": 1,
                    "password": "***********",
                    "picCaptureMode": 3,
                    "picHeight": 1920,
                    "picInterval": 60,
                    "picName": "",
                    "picWidth": 2304,
                    "port": 21,
                    "remoteDir": "hello",
                    "schedule": {
                        "channel": 0, "table": {
                            "AI_DOG_CA T": "111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111",
                            "AI_PEOPLE": "111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111",
                            "AI_VEHICLE": "111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111",
                            "MD": "111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111",
                            "TIMING": "000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
                    } },
                    "server": "192.168.1.236",
                    "streamType": 6,
                    "userName": "ft***er",
                    "videoName": "sdfs"
                } }
        }]
        :return: response
        """
        """
        body = [{
            "action": 0,
            "param": {
                "Ftp": {
                    "password": password,
                    "remoteDir": directory,
                    "server": server_ip,
                    "userName": username,
                }
            }
        }]
        """

        cmd = "SetFtp"
        if self.scheduleVersion == 1:
            cmd = "SetFtpV20"

        body = [
            {
                "cmd": cmd,
                # "action": 0,
                "param": {
                    "Ftp": {
                        "password": password,
                        "remoteDir": directory,
                        "server": server_ip,
                        "userName": username
                    }
                }
            }
        ]
        if self.scheduleVersion == 1:
            body[0]["param"]["Ftp"]["enable"] = int(enable)
        else:
            body[0]["param"]["Ftp"]["schedule"] = { "enable": int(enable) }

        # print(f"Sending {cmd} command: ", body)
        return self._execute_command(cmd, body)

    def set_network_ntp(self, enable: bool, server: str, port: int = 123, interval: int = 1440) -> Dict:
        body = [
            {
                "cmd": "SetNtp",
                # "action": 0,
                "param": {
                    "Ntp": {
                        "enable": int(enable),
                        "server": server,
                        "port": port,
                        "interval": interval
                    }
                }
            }
        ]
        return self._execute_command('SetNtp', body)

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
        cmd = "GetEmail"
        if self.scheduleVersion == 1:
            cmd = "GetEmailV20"
        body = [{"cmd": cmd, "action": 1, "param": { "channel": 0 }}]
        return self._execute_command(cmd, body)

    def set_network_email(self, enable: bool) -> Dict:
        cmd = "SetEmail"
        if self.scheduleVersion == 1:
            cmd = "SetEmailV20"

        body = [ { "cmd": cmd,
                    "param": {
                        "Email": {
                            }
                        }
                  }
                ]

        if self.scheduleVersion == 1:
            body[0]["param"]["Email"]["enable"] = int(enable)
        else:
            body[0]["param"]["Email"]["schedule"] = { "enable": int(enable) }
        return self._execute_command('SetEmail', body)

    def get_network_ftp(self) -> Dict:
        """
        Get the camera FTP network information
        See examples/response/GetNetworkFtp.json for example response data.
        :return: response json
        """
        cmd = "GetFtp"
        if self.scheduleVersion == 1:
            cmd = "GetFtpV20"
        body = [{"cmd": cmd, "action": 0, "param": {}}]
        return self._execute_command(cmd, body)

    def get_network_push(self) -> Dict:
        """
        Get the camera push network information
        See examples/response/GetNetworkPush.json for example response data.
        :return: response json
        """
        cmd = "GetPush"
        if self.scheduleVersion == 1:
            cmd = "GetPushV20"
        body = [{"cmd": cmd, "action": 0, "param": {}}]
        return self._execute_command(cmd, body)

    def get_network_status(self) -> Dict:
        """
        Get the camera status network information
        See examples/response/GetNetworkGeneral.json for example response data.
        :return: response json
        """
        return self.get_network_general()
