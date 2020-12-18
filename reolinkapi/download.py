class DownloadAPIMixin:
    """API calls for downloading video files."""
    def get_file(self, filename: str, output_path: str) -> bool:
        """
        Download the selected video file
        :return: response json
        """
        body = [
            {
                "cmd": "Download",
                "source": filename,
                "output": filename,
                "filepath": output_path
            }
        ]
        resp = self._execute_command('Download', body)

        return resp
