<h1 align="center"> Reolink Python Api Client </h1>

<p align="center">
 <img alt="GitHub" src="https://img.shields.io/github/license/ReolinkCameraApi/reolink-python-api?style=flat-square">
 <img alt="GitHub tag (latest SemVer)" src="https://img.shields.io/github/v/tag/ReolinkCameraApi/reolink-python-api?style=flat-square">
 <img alt="PyPI" src="https://img.shields.io/pypi/v/reolink-api?style=flat-square">
</p>

---

A Reolink Camera client written in Python. 

Other Supported Languages:
 - Go: [reolink-go-api](https://github.com/ReolinkCameraAPI/reolink-go-api)

### Join us on Discord

    https://discord.gg/8z3fdAmZJP

### Purpose

This repository's purpose is to deliver a complete API for the Reolink Camera's, ( TESTED on RLC-411WS )


### But Reolink gives an API in their documentation

Not really. They only deliver a really basic API to retrieve Image data and Video data.

### How?

You can get the Restful API calls by looking through the HTTP Requests made the camera web console. I use Google Chrome developer mode (ctr + shift + i) -> Network.

### Get started

Implement a "Camera" object by passing it an IP address, Username and Password. By instantiating the object, it will try retrieve a login token from the Reolink Camera. This token is necessary to interact with the Camera using other commands.

See the `examples` directory.

### Using the library as a Python Module

Install the package via Pip

    pip install reolink-api==0.0.5

## Contributors

---

### Styling and Standards

This project intends to stick with [PEP8](https://www.python.org/dev/peps/pep-0008/)

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
