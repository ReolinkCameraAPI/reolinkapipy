from typing import Union, List, Dict
from datetime import datetime as dt


# Type hints for input and output of the motion api response
RAW_MOTION_LIST_TYPE = List[Dict[str, Union[str, float, Dict[str, str]]]]
PROCESSED_MOTION_LIST_TYPE = List[Dict[str, Union[str, dt]]]


class MotionAPIMixin:
    """API calls for past motion alerts."""
    def get_motion_files(self, start: dt, end: dt = dt.now(),
                         streamtype: str = 'sub') -> PROCESSED_MOTION_LIST_TYPE:
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

        resp = self._execute_command('Search', body)[0]
        if 'value' not in resp:
            return []
        values = resp['value']
        if 'SearchResult' not in values:
            return []
        result = values['SearchResult']
        files = result.get('File', [])
        if len(files) > 0:
            # Begin processing files
            processed_files = self._process_motion_files(files)
            return processed_files
        return []

    @staticmethod
    def _process_motion_files(motion_files: RAW_MOTION_LIST_TYPE) -> PROCESSED_MOTION_LIST_TYPE:
        """Processes raw list of dicts containing motion timestamps
        and the filename associated with them"""
        # Process files
        processed_motions = []
        replace_fields = {'mon': 'month', 'sec': 'second', 'min': 'minute'}
        for file in motion_files:
            time_range = {}
            for x in ['Start', 'End']:
                # Get raw dict
                raw = file[f'{x}Time']
                # Replace certain keys
                for k, v in replace_fields.items():
                    if k in raw.keys():
                        raw[v] = raw.pop(k)
                time_range[x.lower()] = dt(**raw)
            start, end = time_range.values()
            processed_motions.append({
                'start': start,
                'end': end,
                'filename': file['name']
            })
        return processed_motions
