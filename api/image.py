
class ImageAPIMixin:
    """API calls for image settings."""

    def set_advanced_imaging(self,
                             anti_flicker='Outdoor',
                             exposure='Auto',
                             gain_min=1,
                             gain_max=62,
                             shutter_min=1,
                             shutter_max=125,
                             blue_gain=128,
                             red_gain=128,
                             white_balance='Auto',
                             day_night='Auto',
                             back_light='DynamicRangeControl',
                             blc=128,
                             drc=128,
                             rotation=0,
                             mirroring=0,
                             nr3d=1) -> object:
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
