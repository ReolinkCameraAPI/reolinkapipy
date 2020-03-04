class ZoomAPIMixin:
    """
    API for zooming and changing focus.
    Note that the API does not allow zooming/focusing by absolute
    values rather that changing focus/zoom for a given time.
    """
    def _start_zoom(self, direction, speed=60):
        op = 'ZoomInc' if direction == 'in' else 'ZoomDec'
        data = [{"cmd": "PtzCtrl", "action": 0, "param": {"channel": 0, "op": op, "speed": speed}}]
        return self._execute_command('PtzCtrl', data)

    def start_zoom_in(self, speed=60):
        """
        The camera zooms in until self.stop_zoom() is called.
        :return: response json
        """
        return self._start_zoom('in', speed=speed)

    def start_zoom_out(self, speed=60):
        """
        The camera zooms out until self.stop_zoom() is called.
        :return: response json
        """
        return self._start_zoom('out', speed=speed)

    def stop_zoom(self):
        """
        Stop zooming.
        :return: response json
        """
        data = [{"cmd": "PtzCtrl", "action": 0, "param": {"channel": 0, "op": "Stop"}}]
        return self._execute_command('PtzCtrl', data)
