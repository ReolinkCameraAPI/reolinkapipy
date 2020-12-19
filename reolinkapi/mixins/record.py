from typing import Dict


class RecordAPIMixin:
    """API calls for the recording settings"""

    def get_recording_encoding(self) -> Dict:
        """
        Get the current camera encoding settings for "Clear" and "Fluent" profiles.
        See examples/response/GetEnc.json for example response data.
        :return: response json
        """
        body = [{"cmd": "GetEnc", "action": 1, "param": {"channel": 0}}]
        return self._execute_command('GetEnc', body)

    def get_recording_advanced(self) -> Dict:
        """
        Get recording advanced setup data
        See examples/response/GetRec.json for example response data.
        :return: response json
        """
        body = [{"cmd": "GetRec", "action": 1, "param": {"channel": 0}}]
        return self._execute_command('GetRec', body)

    def set_recording_encoding(self,
                               audio: float = 0,
                               main_bit_rate: float = 8192,
                               main_frame_rate: float = 8,
                               main_profile: str = 'High',
                               main_size: str = "2560*1440",
                               sub_bit_rate: float = 160,
                               sub_frame_rate: float = 7,
                               sub_profile: str = 'High',
                               sub_size: str = '640*480') -> Dict:
        """
        Sets the current camera encoding settings for "Clear" and "Fluent" profiles.
        :param audio: int Audio on or off
        :param main_bit_rate: int Clear Bit Rate
        :param main_frame_rate: int Clear Frame Rate
        :param main_profile: string Clear Profile
        :param main_size: string Clear Size
        :param sub_bit_rate: int Fluent Bit Rate
        :param sub_frame_rate: int Fluent Frame Rate
        :param sub_profile: string Fluent Profile
        :param sub_size: string Fluent Size
        :return: response
        """
        body = [
            {
                "cmd": "SetEnc",
                "action": 0,
                "param": {
                    "Enc": {
                        "audio": audio,
                        "channel": 0,
                        "mainStream": {
                            "bitRate": main_bit_rate,
                            "frameRate": main_frame_rate,
                            "profile": main_profile,
                            "size": main_size
                        },
                        "subStream": {
                            "bitRate": sub_bit_rate,
                            "frameRate": sub_frame_rate,
                            "profile": sub_profile,
                            "size": sub_size
                        }
                    }
                }
            }
        ]
        return self._execute_command('SetEnc', body)
