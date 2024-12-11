class DownloadAPIMixin:
    """API calls for downloading video files."""
    def get_file(self, filename: str, output_path: str, method = 'Playback') -> bool:
        """
        Download the selected video file
        On at least Trackmix Wifi, it was observed that the Playback method
        yields much improved download speeds over the Download method, for
        unknown reasons.
        :return: response json
        """
        body = [
            {
                "cmd": method,
                "source": filename,
                "output": filename,
                "filepath": output_path
            }
        ]
        resp = self._execute_command(method, body)

        return resp
