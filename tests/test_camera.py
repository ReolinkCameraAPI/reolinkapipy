import os
from configparser import RawConfigParser
import unittest
from reolink_api import Camera


def read_config(props_path: str) -> dict:
    """Reads in a properties file into variables.

    NB! this config file is kept out of commits with .gitignore. The structure of this file is such:
    # secrets.cfg
        [camera]
        ip={ip_address}
        username={username}
        password={password}
    """
    config = RawConfigParser()
    assert os.path.exists(props_path), f"Path does not exist: {props_path}"
    config.read(props_path)
    return config


class TestCamera(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.config = read_config('../secrets.cfg')

    def setUp(self) -> None:
        self.cam = Camera(self.config.get('camera', 'ip'), self.config.get('camera', 'username'),
                          self.config.get('camera', 'password'))

    def test_camera(self):
        """Test that camera connects and gets a token"""
        self.assertTrue(self.cam.ip == self.config.get('camera', 'ip'))
        self.assertTrue(self.cam.token != '')


if __name__ == '__main__':
    unittest.main()
