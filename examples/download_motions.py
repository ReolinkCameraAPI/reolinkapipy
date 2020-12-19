"""Downloads all motion events from camera from the past hour."""
import os
from configparser import RawConfigParser
from datetime import datetime as dt, timedelta
from reolinkapi import Camera


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


# Read in your ip, username, & password
#   (NB! you'll likely have to create this file. See tests/test_camera.py for details on structure)
config = read_config('../secrets.cfg')

ip = config.get('camera', 'ip')
un = config.get('camera', 'username')
pw = config.get('camera', 'password')

# Connect to camera
cam = Camera(ip, un, pw)

start = (dt.now() - timedelta(hours=1))
end = dt.now()
# Collect motion events between these timestamps for substream
processed_motions = cam.get_motion_files(start=start, end=end, streamtype='sub')

dl_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
for i, motion in enumerate(processed_motions):
    fname = motion['filename']
    # Download the mp4
    resp = cam.get_file(fname, output_path=os.path.join(dl_dir, f'motion_event_{i}.mp4'))
