from typing import Dict


class DisplayAPIMixin:
    """API calls related to the current image (osd, on screen display)."""

    def get_osd(self) -> Dict:
        """
        Get OSD information.
        See examples/response/GetOsd.json for example response data.
        :return: response json
        """
        body = [{"cmd": "GetOsd", "action": 1, "param": {"channel": 0}}]
        return self._execute_command('GetOsd', body)

    def get_mask(self) -> Dict:
        """
        Get the camera mask information.
        See examples/response/GetMask.json for example response data.
        :return: response json
        """
        body = [{"cmd": "GetMask", "action": 1, "param": {"channel": 0}}]
        return self._execute_command('GetMask', body)

    def set_osd(self, bg_color: bool = 0, channel: float = 0, osd_channel_enabled: bool = 0,
                osd_channel_name: str = "", osd_channel_pos: str = "Lower Right", osd_time_enabled: bool = 0,
                osd_time_pos: str = "Lower Right", osd_watermark_enabled: bool = 0) -> bool:
        """
        Set OSD
        :param bg_color: bool
        :param channel: int channel id
        :param osd_channel_enabled: bool
        :param osd_channel_name: string channel name
        :param osd_channel_pos: string channel position
            ["Upper Left","Top Center","Upper Right","Lower Left","Bottom Center","Lower Right"]
        :param osd_time_enabled: bool
        :param osd_time_pos: string time position
            ["Upper Left","Top Center","Upper Right","Lower Left","Bottom Center","Lower Right"]
        :return: whether the action was successful
        """
        body = [{"cmd": "SetOsd", "action": 1,
                 "param": {
                    "Osd": {
                        "bgcolor": bg_color,
                        "channel": channel,
                        "osdChannel": {
                            "enable": osd_channel_enabled, "name": osd_channel_name,
                            "pos": osd_channel_pos
                        },
                        "osdTime": {"enable": osd_time_enabled, "pos": osd_time_pos},
                        "watermark": osd_watermark_enabled,
                    }}}]
        r_data = self._execute_command('SetOsd', body)[0]
        if 'value' in r_data and r_data["value"]["rspCode"] == 200:
            return True
        print("Could not set OSD. Camera responded with status:", r_data["error"])
        return False
