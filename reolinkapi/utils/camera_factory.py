import asyncio
from typing import List

from pyphorus.devices import Device

from reolinkapi import Camera


class CameraFactory:

    def __init__(self, username="admin", password=""):
        self._username = username
        self._password = password
        self._cameras = []

    @property
    def cameras(self):
        return self._cameras

    def get_cameras_from_devices(self, devices: List[Device]) -> List[Camera]:
        # only get the ip from each device

        ips = []
        for device in devices:
            ips.append(device.ip)

        for ip in ips:
            self._cameras.append(Camera(ip, self._username, self._password, defer_login=True))

        return self._cameras

    def initialise_cameras(self, timeout: int = 2):
        if len(self._cameras) == 0:
            raise Exception("there are no cameras in camera factory")

        async def _initialise_camera():
            tasks = []
            for camera in self._cameras:
                tasks.append(asyncio.wait_for(camera.login(), timeout=timeout))

            await asyncio.gather(*tasks)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(_initialise_camera())
