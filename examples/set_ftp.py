#!/opt/homebrew/bin/python3

import reolinkapi
import os
import json
from sys import argv

def ftp_cam(which):
    hostname = 'watchdog%d' % which
    cam_name = 'Watchdog%d' % which

    try:
        cam = reolinkapi.Camera(hostname, username="userid", password="passwd")
    except:
        print(f"Failed to open camera {cam_name}")
        return 1

    if not cam.is_logged_in():
        print(f"Login failed for {cam_name}")
        return 2

    try:
        print(f"Setting FTP params for {cam_name}")
        response = cam.set_network_ftp("hocus", "pocus", "directory", "192.168.1.2", 0)
        print( json.dumps( response, indent=4 ) )
        print( json.dumps( cam.get_network_ftp(), indent=4 ) )
        if response[0]["value"]["rspCode"] == 200:
            print("Success!")
    except Exception as e:
        print(f"{argv[0]} for {cam_name} failed.")
        print(e)
        return 3

    return 0


if __name__ == "__main__":
    if len(argv) != 2:
        print("Usage: %s <cam#>]" % argv[0])
        exit(1)

    exit( ftp_cam(int(argv[1])) )


