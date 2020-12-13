class DownloadAPIMixin:
    """API calls for downloading video files."""
    def get_file(self, filename: str) -> object:
        """
        Download the selected video file
        :return: response json
        """
        body = [
            {
                "cmd": "Download",
                "source": filename,
                "output": filename
            }
        ]
        return self._execute_command('Download', body)
