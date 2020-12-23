import socket
from typing import List

import netaddr
import pyphorus
from pyphorus import Device


class Discover:

    def __init__(self, media_port: int = 9000, onvif_port: int = 8000, rtsp_port: int = 554, rtmp_port: int = 1935,
                 https_port: int = 443, http_port: int = 80, unique_device_ip: bool = True):
        """
        Create a discover object. Pass custom port values to override the standard ones.
        :param media_port:
        :param onvif_port:
        :param rtsp_port:
        :param rtmp_port:
        :param https_port:
        :param http_port:
        :param unique_device_ip: strip duplicate ips (basically ignoring the ports)
        """
        self._unique_device_ip = unique_device_ip
        self._media_port = media_port
        self._onvif_port = onvif_port
        self._rtsp_port = rtsp_port
        self._rtmp_port = rtmp_port
        self._https_port = https_port
        self._http_port = http_port

        self._phorus = pyphorus.Pyphorus()

        self._devices = []

    @property
    def media_port(self):
        return self._media_port

    @property
    def onvif_port(self):
        return self._onvif_port

    @property
    def rtsp_port(self):
        return self._rtsp_port

    @property
    def rtmp_port(self):
        return self._rtmp_port

    @property
    def https_port(self):
        return self._https_port

    @property
    def http_port(self):
        return self._http_port

    def list_standard_ports(self):
        return {
            "http": self._http_port,
            "https": self._https_port,
            "media": self._media_port,
            "onvif": self._onvif_port,
            "rtsp": self._rtsp_port,
            "rtmp": self._rtmp_port,
        }

    def discover_upnp(self) -> List[Device]:
        """
        discover cameras using UPnP
        this will only work if the camera has it enabled
        :return:
        """
        # TODO: unsure about the reolink upnp `st`
        self._devices = self._phorus.scan_upnp("upnp:reolink")

        if self._unique_device_ip:
            self._devices = pyphorus.utils.strip_duplicate_ips(devices=self._devices)

        return self._devices

    def discover_port(self, custom_cidr: str = None, additional_ports: List[int] = None) -> List[Device]:
        """
        discover devices by scanning the network for open ports
        this method will attempt at using the current machines' ip address to scan for open ports, to change
        the ip address, change the custom_cidr field value
        :param custom_cidr: cidr ip e.g. 192.168.0.0/24
        :param additional_ports: a list of additional ports to add [ 9000, 100000, ... ] to the standard or overridden
         ports
        :return:
        """

        if custom_cidr is None:
            # attempt to get this machine's local ip
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            # get the cidr from the ip address
            cidr = netaddr.cidr_merge([ip_address])
            if len(cidr) > 0:
                cidr = cidr[0]
            custom_cidr = cidr

        custom_ports = [self._media_port, self._rtmp_port, self._rtsp_port, self._onvif_port, self._https_port,
                        self._http_port]

        if additional_ports is not None:
            # use the cameras' standard ports
            custom_ports += additional_ports

        self._devices = self._phorus.scan_ports(custom_cidr, ports=custom_ports)

        if self._unique_device_ip:
            self._devices = pyphorus.utils.strip_duplicate_ips(devices=self._devices)

        return self._devices
