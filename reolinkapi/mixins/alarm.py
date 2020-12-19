from typing import Dict


class AlarmAPIMixin:
    """API calls for getting device alarm information."""

    def get_alarm_motion(self) -> Dict:
        """
        Gets the device alarm motion
        See examples/response/GetAlarmMotion.json for example response data.
        :return: response json
        """
        body = [{"cmd": "GetAlarm", "action": 1, "param": {"Alarm": {"channel": 0, "type": "md"}}}]
        return self._execute_command('GetAlarm', body)
