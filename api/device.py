class DeviceAPIMixin:
    """API calls for getting device information."""
    def get_hdd_info(self) -> object:
        """
        Gets all HDD and SD card information from Camera
        See examples/response/GetHddInfo.json for example response data.
        :return: response json
        """
        body = [{"cmd": "GetHddInfo", "action": 0, "param": {}}]
        return self._execute_command('GetHddInfo', body)

    def format_hdd(self, hdd_id: [int] = [0]) -> bool:
        """
        Format specified HDD/SD cards with their id's
        :param hdd_id: List of id's specified by the camera with get_hdd_info api. Default is 0 (SD card)
        :return: bool
        """
        body = [{"cmd": "Format", "action": 0, "param": {"HddInfo": {"id": hdd_id}}}]
        r_data = self._execute_command('Format', body)
        if r_data["value"]["rspCode"] == "200":
            return True
        print("Could not format HDD/SD. Camera responded with:", r_data["value"])
        return False
