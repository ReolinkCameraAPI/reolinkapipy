<h1 align="center"> Reolink Python Api Client </h1>

<p align="center">
 <img alt="Reolink Approval" src="https://img.shields.io/badge/reolink-approved-blue?style=flat-square">
 <img alt="GitHub" src="https://img.shields.io/github/license/ReolinkCameraAPI/reolinkapipy?style=flat-square">
 <img alt="GitHub tag (latest SemVer)" src="https://img.shields.io/github/v/tag/ReolinkCameraAPI/reolinkapipy?style=flat-square">
 <img alt="PyPI" src="https://img.shields.io/pypi/v/reolinkapi?style=flat-square">
 <img alt="Discord" src="https://img.shields.io/discord/773257004911034389?style=flat-square">
</p>

---

A Reolink Camera client written in Python. This repository's purpose **(with Reolink's full support)** is to deliver a complete API for the Reolink Cameras,
although they have a basic API document - it does not satisfy the need for extensive camera communication.

Check out our documentation for more information on how to use the software at [https://reolink.oleaintueri.com](https://reolink.oleaintueri.com)


Other Supported Languages:
 - Go: [reolinkapigo](https://github.com/ReolinkCameraAPI/reolinkapigo)

### Join us on Discord

    https://discord.gg/8z3fdAmZJP
    

### Sponsorship

<a href="https://oleaintueri.com"><img src="https://oleaintueri.com/images/oliv.svg" width="60px"/><img width="200px" style="padding-bottom: 10px" src="https://oleaintueri.com/images/oleaintueri.svg"/></a>

[Oleaintueri](https://oleaintueri.com) is sponsoring the development and maintenance of these projects within their organisation.


---

### Get started

Implement a "Camera" object by passing it an IP address, Username and Password. By instantiating the object, it will try retrieve a login token from the Reolink Camera. This token is necessary to interact with the Camera using other commands.

See the `examples` directory.

### Installation

Install the package via PyPi

    pip install reolinkapi

Install from GitHub

    pip install git+https://github.com/ReolinkCameraAPI/reolinkapipy.git
    
### Usage

```python

import reolinkapi

if __name__ == "__main__":
    # this will immediately log in with default camera credentials
    cam = reolinkapi.Camera("192.168.0.100")

    # OR in the case of managing a pool of cameras' - it's better to defer login 
    # foo is the username
    # bar is the password
    _ = reolinkapi.Camera("192.168.0.100", "foo", "bar", defer_login = True)

    # to scan your network for reolink cameras
    
    # when UPnP is enabled on the camera, simply use:
    discovery = reolinkapi.Discover()
    devices = discovery.discover_upnp()

    # OR
    _ = discovery.discover_port()

    # when many cameras share the same credentials
    # foo is the username
    # bar is the password
    factory = reolinkapi.CameraFactory(username="foo", password="bar")
    _ = factory.get_cameras_from_devices(devices)

    # when using the CameraFactory, we need to log in manually on each camera
    # since it creates a pool of cameras
    # one can use the utility function in camera factory to run an asyncio task
    factory.initialise_cameras()

    # now one can check if the camera has been initialised
    for camera in factory.cameras:
        if camera.is_loggedin():
            print(f'Camera {camera.ip} is logged in')
        else:
            print(f'Camera {camera.ip} is NOT logged in')
```
## Contributors

---

### Styling and Standards

This project intends to stick with [PEP8](https://www.python.org/dev/peps/pep-0008/)

### How can I become a contributor?

#### Step 1

Get the Restful API calls by looking through the HTTP Requests made in the camera's web UI. I use Google Chrome developer mode (ctr + shift + i) -> Network.

#### Step 2

- Fork the repository
- pip install -r requirements.txt
- Make your changes

#### Step 3

Make a pull request.

### API Requests Implementation Plan:

Stream:
- [X] Blocking RTSP stream
- [X] Non-Blocking RTSP stream

GET:
- [X] Login
- [X] Logout
- [X] Display -> OSD
- [X] Recording -> Encode (Clear and Fluent Stream)
- [X] Recording -> Advance (Scheduling)
- [X] Network -> General
- [X] Network -> Advanced
- [X] Network -> DDNS
- [X] Network -> NTP
- [X] Network -> E-mail
- [X] Network -> FTP
- [X] Network -> Push
- [X] Network -> WIFI
- [X] Alarm -> Motion
- [X] System -> General
- [X] System -> DST
- [X] System -> Information
- [ ] System -> Maintenance
- [X] System -> Performance
- [ ] System -> Reboot
- [X] User -> Online User
- [X] User -> Add User
- [X] User -> Manage User
- [X] Device -> HDD/SD Card
- [ ] Zoom
- [ ] Focus
- [ ] Image (Brightness, Contrast, Saturation, Hue, Sharp, Mirror, Rotate)
- [ ] Advanced Image (Anti-flicker, Exposure, White Balance, DayNight, Backlight, LED light, 3D-NR)
- [X] Image Data -> "Snap" Frame from Video Stream

SET:
- [X] Display -> OSD
- [X] Recording -> Encode (Clear and Fluent Stream)
- [ ] Recording -> Advance (Scheduling)
- [X] Network -> General
- [X] Network -> Advanced
- [ ] Network -> DDNS
- [ ] Network -> NTP
- [ ] Network -> E-mail
- [ ] Network -> FTP
- [ ] Network -> Push
- [X] Network -> WIFI
- [ ] Alarm -> Motion
- [ ] System -> General
- [ ] System -> DST
- [X] System -> Reboot
- [X] User -> Online User
- [X] User -> Add User
- [X] User -> Manage User
- [X] Device -> HDD/SD Card (Format)
- [x] PTZ
- [x] Zoom
- [x] Focus
- [X] Image (Brightness, Contrast, Saturation, Hue, Sharp, Mirror, Rotate)
- [X] Advanced Image (Anti-flicker, Exposure, White Balance, DayNight, Backlight, LED light, 3D-NR)

### Supported Cameras

Any Reolink camera that has a web UI should work. The other's requiring special Reolink clients
do not work and is not supported here.

- RLC-411WS
- RLC-423
- RLC-420-5MP
- RLC-410-5MP
- RLC-520
