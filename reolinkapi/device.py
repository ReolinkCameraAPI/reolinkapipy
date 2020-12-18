from typing import List, Dict


class DeviceAPIMixin:
    """API calls for getting device information."""
    DEFAULT_HDD_ID = [0]

    def get_hdd_info(self) -> Dict:
        """
        Gets all HDD and SD card information from Camera
        See examples/response/GetHddInfo.json for example response data.
        :return: response json
        """
        body = [{"cmd": "GetHddInfo", "action": 0, "param": {}}]
        return self._execute_command('GetHddInfo', body)

    def format_hdd(self, hdd_id: List[float] = None) -> bool:
        """
        Format specified HDD/SD cards with their id's
        :param hdd_id: List of id's specified by the camera with get_hdd_info api. Default is 0 (SD card)
        :return: bool
        """
        if hdd_id is None:
            hdd_id = self.DEFAULT_HDD_ID
        body = [{"cmd": "Format", "action": 0, "param": {"HddInfo": {"id": hdd_id}}}]
        r_data = self._execute_command('Format', body)[0]
        if r_data["value"]["rspCode"] == 200:
            return True
        print("Could not format HDD/SD. Camera responded with:", r_data["value"])
        return False
