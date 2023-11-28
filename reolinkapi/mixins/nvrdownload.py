from datetime import datetime as dt

class NvrDownloadAPIMixin:
    """API calls for NvrDownload."""
    def get_playback_files(self, start: dt, end: dt = dt.now(), channel: int = 0,
                         streamtype: str = 'sub'):
        """
        Get the filenames of the videos for the time range provided.

        Args:
            start: the starting time range to examine
            end: the end time of the time range to examine
            channel: which channel to download from
            streamtype: 'main' or 'sub' - the stream to examine
        :return: response json
        """
        search_params = {
            'NvrDownload': {
                'channel': channel,
                'iLogicChannel': 0,
                'streamType': streamtype,
                'StartTime': {
                    'year': start.year,
                    'mon': start.month,
                    'day': start.day,
                    'hour': start.hour,
                    'min': start.minute,
                    'sec': start.second
                },
                'EndTime': {
                    'year': end.year,
                    'mon': end.month,
                    'day': end.day,
                    'hour': end.hour,
                    'min': end.minute,
                    'sec': end.second
                }
            }
        }
        body = [{"cmd": "NvrDownload", "action": 1, "param": search_params}]

        resp = self._execute_command('NvrDownload', body)[0]
        if 'value' not in resp:
            return []
        values = resp['value']
        if 'fileList' not in values:
            return []
        files = values['fileList']
        if len(files) > 0:
            return [file['fileName'] for file in files]
        return []
