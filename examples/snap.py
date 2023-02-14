#!/opt/homebrew/bin/python3

import reolinkapi
import os
from sys import argv

def snap_cam(which, dirname):
    hostname = 'watchdog%d' % which
    cam_name = 'Watchdog%d' % which

    try:
        cam = reolinkapi.Camera(hostname, username="rtsp", password="darknet")
    except:
        print(f"Failed to open camera {cam_name}")
        return 1

    if not cam.is_logged_in():
        print(f"Login failed for {cam_name}")
        return 2

    image_file = '%s/%s.jpg' % (dirname, hostname)
    if os.path.exists(image_file):
        os.unlink(image_file)

    print("Snapping", cam_name)
    image = cam.get_snap()
    image.save(image_file)
    return 0


if __name__ == "__main__":
    dirname = '.'
    if len(argv) == 3:
        dirname = argv[2]
    elif len(argv) != 2:
        print("Usage: %s <cam#> [output-directory]" % argv[0])
        exit(1)

    exit( snap_cam(int(argv[1]), dirname) )


