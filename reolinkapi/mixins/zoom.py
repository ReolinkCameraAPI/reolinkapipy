from typing import Dict


class ZoomAPIMixin:
    """
    API for zooming and changing focus.
    Note that the API does not allow zooming/focusing by absolute
    values rather that changing focus/zoom for a given time.
    """
    def _start_operation(self, operation: str, speed: float) -> Dict:
        data = [{"cmd": "PtzCtrl", "action": 0, "param": {"channel": 0, "op": operation, "speed": speed}}]
        return self._execute_command('PtzCtrl', data)

    def _stop_zooming_or_focusing(self) -> Dict:
        """This command stops any ongoing zooming or focusing actions."""
        data = [{"cmd": "PtzCtrl", "action": 0, "param": {"channel": 0, "op": "Stop"}}]
        return self._execute_command('PtzCtrl', data)

    def start_zooming_in(self, speed: float = 60) -> Dict:
        """
        The camera zooms in until self.stop_zooming() is called.
        :return: response json
        """
        return self._start_operation('ZoomInc', speed=speed)

    def start_zooming_out(self, speed: float = 60) -> Dict:
        """
        The camera zooms out until self.stop_zooming() is called.
        :return: response json
        """
        return self._start_operation('ZoomDec', speed=speed)

    def stop_zooming(self) -> Dict:
        """
        Stop zooming.
        :return: response json
        """
        return self._stop_zooming_or_focusing()

    def start_focusing_in(self, speed: float = 32) -> Dict:
        """
        The camera focuses in until self.stop_focusing() is called.
        :return: response json
        """
        return self._start_operation('FocusInc', speed=speed)

    def start_focusing_out(self, speed: float = 32) -> Dict:
        """
        The camera focuses out until self.stop_focusing() is called.
        :return: response json
        """
        return self._start_operation('FocusDec', speed=speed)

    def stop_focusing(self) -> Dict:
        """
        Stop focusing.
        :return: response json
        """
        return self._stop_zooming_or_focusing()
