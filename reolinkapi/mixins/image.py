from typing import Dict


class ImageAPIMixin:
    """API calls for image settings."""

    def set_adv_image_settings(self,
                               anti_flicker: str = 'Outdoor',
                               exposure: str = 'Auto',
                               gain_min: float = 1,
                               gain_max: float = 62,
                               shutter_min: float = 1,
                               shutter_max: float = 125,
                               blue_gain: float = 128,
                               red_gain: float = 128,
                               white_balance: str = 'Auto',
                               day_night: str = 'Auto',
                               back_light: str = 'DynamicRangeControl',
                               blc: float = 128,
                               drc: float = 128,
                               rotation: float = 0,
                               mirroring: float = 0,
                               nr3d: float = 1) -> Dict:
        """
        Sets the advanced camera settings.

        :param anti_flicker: string
        :param exposure: string
        :param gain_min: int
        :param gain_max: string
        :param shutter_min: int
        :param shutter_max: int
        :param blue_gain: int
        :param red_gain: int
        :param white_balance: string
        :param day_night: string
        :param back_light: string
        :param blc: int
        :param drc: int
        :param rotation: int
        :param mirroring: int
        :param nr3d: int
        :return: response
        """
        body = [{
            "cmd": "SetIsp",
            "action": 0,
            "param": {
                "Isp": {
                    "channel": 0,
                    "antiFlicker": anti_flicker,
                    "exposure": exposure,
                    "gain": {"min": gain_min, "max": gain_max},
                    "shutter": {"min": shutter_min, "max": shutter_max},
                    "blueGain": blue_gain,
                    "redGain": red_gain,
                    "whiteBalance": white_balance,
                    "dayNight": day_night,
                    "backLight": back_light,
                    "blc": blc,
                    "drc": drc,
                    "rotation": rotation,
                    "mirroring": mirroring,
                    "nr3d": nr3d
                }
            }
        }]
        return self._execute_command('SetIsp', body)

    def set_image_settings(self,
                           brightness: float = 128,
                           contrast: float = 62,
                           hue: float = 1,
                           saturation: float = 125,
                           sharpness: float = 128) -> Dict:
        """
        Sets the camera image settings.

        :param brightness: int
        :param contrast: string
        :param hue: int
        :param saturation: int
        :param sharpness: int
        :return: response
        """
        body = [
            {
                "cmd": "SetImage",
                "action": 0,
                "param": {
                    "Image": {
                        "bright": brightness,
                        "channel": 0,
                        "contrast": contrast,
                        "hue": hue,
                        "saturation": saturation,
                        "sharpen": sharpness
                    }
                }
            }
        ]

        return self._execute_command('SetImage', body)
