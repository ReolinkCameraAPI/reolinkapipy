from typing import Dict


class AlarmAPIMixin:
    """API calls for getting device alarm information."""

    def get_alarm(self) -> Dict:
        """
        Gets the device alarm motion
        See examples/response/GetAlarmMotion.json for example response data.
        :return: response json
        """
        cmd = "GetAlarm"
        body = [{"cmd": cmd, "action": 1, "param": {"Alarm": {"channel": 0, "type": "md"}}}]
        return self._execute_command(cmd, body)

    def get_alarm_motion(self) -> Dict:
        """
        Gets the device alarm motion
        See examples/response/GetAlarmMotion.json for example response data.
        :return: response json
        """
        cmd = "GetMdAlarm"
        body = [{"cmd": cmd, "action": 1, "param": {"channel": 0}}]
        return self._execute_command(cmd, body)
