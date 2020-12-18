<h1 align="center"> Reolink Python Api Client </h1>

<p align="center">
 <img alt="Reolink Approval" src="https://img.shields.io/badge/reolink-approved-blue?style=flat-square">
 <img alt="GitHub" src="https://img.shields.io/github/license/ReolinkCameraApi/reolink-python-api?style=flat-square">
 <img alt="GitHub tag (latest SemVer)" src="https://img.shields.io/github/v/tag/ReolinkCameraApi/reolink-python-api?style=flat-square">
 <img alt="PyPI" src="https://img.shields.io/pypi/v/reolink-api?style=flat-square">
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

### Using the library as a Python Module

Install the package via Pip

    pip install reolink-api==0.0.5

Install from GitHub

    pip install git+https://github.com/ReolinkCameraAPI/reolink-python-api.git
    
## Contributors

---

### Styling and Standards

This project intends to stick with [PEP8](https://www.python.org/dev/peps/pep-0008/)

### How can I become a contributor?

#### Step 1

Get the Restful API calls by looking through the HTTP Requests made in the camera's web UI. I use Google Chrome developer mode (ctr + shift + i) -> Network.

#### Step 2

Fork the repository and make your changes.

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
