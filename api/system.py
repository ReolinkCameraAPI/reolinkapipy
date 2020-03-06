class SystemAPIMixin:
    """API for accessing general system information of the camera."""
    def get_general_system(self) -> object:
        """:return: response json"""
        body = [{"cmd": "GetTime", "action": 1, "param": {}}, {"cmd": "GetNorm", "action": 1, "param": {}}]
        return self._execute_command('get_general_system', body, multi=True)

    def get_performance(self) -> object:
        """
        Get a snapshot of the current performance of the camera.
        See examples/response/GetPerformance.json for example response data.
        :return: response json
        """
        body = [{"cmd": "GetPerformance", "action": 0, "param": {}}]
        return self._execute_command('GetPerformance', body)

    def get_information(self) -> object:
        """
        Get the camera information
        See examples/response/GetDevInfo.json for example response data.
        :return: response json
        """
        body = [{"cmd": "GetDevInfo", "action": 0, "param": {}}]
        return self._execute_command('GetDevInfo', body)

    def reboot_camera(self) -> object:
        """
        Reboots the camera
        :return: response json
        """
        body = [{"cmd": "Reboot", "action": 0, "param": {}}]
        return self._execute_command('Reboot', body)
