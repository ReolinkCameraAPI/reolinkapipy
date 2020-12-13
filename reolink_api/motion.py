from datetime import datetime as dt


class MotionAPIMixin:
    """API calls for past motion alerts."""
    def get_motion_files(self, start: dt, end: dt = dt.now(),
                         streamtype: str = 'main') -> object:
        """
        Get the timestamps and filenames of motion detection events for the time range provided.

        Args:
            start: the starting time range to examine
            end: the end time of the time range to examine
            streamtype: 'main' or 'sub' - the stream to examine
        :return: response json
        """
        search_params = {
            'Search': {
                'channel': 0,
                'streamType': streamtype,
                'onlyStatus': 0,
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
        body = [{"cmd": "Search", "action": 1, "param": search_params}]
        return self._execute_command('Search', body)
