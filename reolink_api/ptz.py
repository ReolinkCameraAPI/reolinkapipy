from typing import Dict


class PtzAPIMixin:
    """
    API for PTZ functions.
    """
    def _send_operation(self, operation: str, speed: float, index: float = None) -> Dict:
        # Refactored to reduce redundancy
        param = {"channel": 0, "op": operation, "speed": speed}
        if index is not None:
            param['id'] = index
        data = [{"cmd": "PtzCtrl", "action": 0, "param": param}]
        return self._execute_command('PtzCtrl', data)

    def _send_noparm_operation(self, operation: str) -> Dict:
        data = [{"cmd": "PtzCtrl", "action": 0, "param": {"channel": 0, "op": operation}}]
        return self._execute_command('PtzCtrl', data)

    def _send_set_preset(self, enable: float, preset: float = 1, name: str = 'pos1') -> Dict:
        data = [{"cmd": "SetPtzPreset", "action": 0, "param": {
            "channel": 0, "enable": enable, "id": preset, "name": name}}]
        return self._execute_command('PtzCtrl', data)

    def go_to_preset(self, speed: float = 60, index: float = 1) -> Dict:
        """
        Move the camera to a preset location
        :return: response json
        """
        return self._send_operation('ToPos', speed=speed, index=index)

    def add_preset(self, preset: float = 1, name: str = 'pos1') -> Dict:
        """
        Adds the current camera position to the specified preset.
        :return: response json
        """
        return self._send_set_preset(enable=1, preset=preset, name=name)

    def remove_preset(self, preset: float = 1, name: str = 'pos1') -> Dict:
        """
        Removes the specified preset
        :return: response json
        """
        return self._send_set_preset(enable=0, preset=preset, name=name)

    def move_right(self, speed: float = 25) -> Dict:
        """
        Move the camera to the right
        The camera moves self.stop_ptz() is called.
        :return: response json
        """
        return self._send_operation('Right', speed=speed)

    def move_right_up(self, speed: float = 25) -> Dict:
        """
        Move the camera to the right and up
        The camera moves self.stop_ptz() is called.
        :return: response json
        """
        return self._send_operation('RightUp', speed=speed)

    def move_right_down(self, speed: float = 25) -> Dict:
        """
        Move the camera to the right and down
        The camera moves self.stop_ptz() is called.
        :return: response json
        """
        return self._send_operation('RightDown', speed=speed)

    def move_left(self, speed: float = 25) -> Dict:
        """
        Move the camera to the left
        The camera moves self.stop_ptz() is called.
        :return: response json
        """
        return self._send_operation('Left', speed=speed)

    def move_left_up(self, speed: float = 25) -> Dict:
        """
        Move the camera to the left and up
        The camera moves self.stop_ptz() is called.
        :return: response json
        """
        return self._send_operation('LeftUp', speed=speed)

    def move_left_down(self, speed: float = 25) -> Dict:
        """
        Move the camera to the left and down
        The camera moves self.stop_ptz() is called.
        :return: response json
        """
        return self._send_operation('LeftDown', speed=speed)

    def move_up(self, speed: float = 25) -> Dict:
        """
        Move the camera up.
        The camera moves self.stop_ptz() is called.
        :return: response json
        """
        return self._send_operation('Up', speed=speed)

    def move_down(self, speed: float = 25) -> Dict:
        """
        Move the camera down.
        The camera moves self.stop_ptz() is called.
        :return: response json
        """
        return self._send_operation('Down', speed=speed)

    def stop_ptz(self) -> Dict:
        """
        Stops the cameras current action.
        :return: response json
        """
        return self._send_noparm_operation('Stop')

    def auto_movement(self, speed: float = 25) -> Dict:
        """
        Move the camera in a clockwise rotation.
        The camera moves self.stop_ptz() is called.
        :return: response json
        """
        return self._send_operation('Auto', speed=speed)
