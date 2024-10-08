import os
from configparser import RawConfigParser
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
config = read_config('camera.cfg')

ip = config.get('camera', 'ip')
un = config.get('camera', 'username')
pw = config.get('camera', 'password')

# Connect to camera
cam = Camera(ip, un, pw)

# Set NTP
cam.set_ntp(enable=True, interval=1440, port=123, server="time-b.nist.gov")

# Get current network settings
current_settings = cam.get_network_general()
print("Current settings:", current_settings)

# Configure DHCP
cam.set_network_settings(
    ip="",
    gateway="",
    mask="",
    dns1="",
    dns2="",
    mac=current_settings[0]['value']['LocalLink']['mac'],
    use_dhcp=True,
    auto_dns=True
)

# Configure static IP
# cam.set_network_settings(
#     ip="192.168.1.102",
#     gateway="192.168.1.1",
#     mask="255.255.255.0",
#     dns1="8.8.8.8",
#     dns2="8.8.4.4",
#     mac=current_settings[0]['value']['LocalLink']['mac'],
#     use_dhcp=False,
#     auto_dns=False
# )