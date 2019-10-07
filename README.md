## ReolinkCameraAPI

### Purpose

This repository's purpose is to deliver a complete API for the Reolink Camera's, ( TESTED on RLC-411WS )


### But Reolink gives an API in their documentation

Not really. They only deliver a really basic API to retrieve Image data and Video data.

### How?

You can get the Restful API calls by looking through the HTTP Requests made the camera web console. I use Google Chrome developer mode (ctr + shift + i) -> Network.

### Get started

Implement a "Camera" object by passing it an IP address, Username and Password. By instantiating the object, it will try retrieve a login token from the Reolink Camera. This token is necessary to interact with the Camera using other commands.

### Styling and Standards

This project intends to stick with [PEP8](https://www.python.org/dev/peps/pep-0008/)

### API Requests Implementation Plan:

GET:
- [X] Login
- [ ] Display -> OSD
- [ ] Recording -> Encode (Clear and Fluent Stream)
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
- [X] System -> General
- [ ] System -> DST
- [ ] System -> Information
- [ ] System -> Maintenance
- [ ] System -> Performance
- [ ] System -> Reboot
- [ ] User -> Online User
- [ ] User -> Add User
- [ ] User -> Manage User
- [ ] Device -> HDD/SD Card
- [ ] Zoom
- [ ] Focus
- [ ] Image (Brightness, Contrass, Saturation, Hue, Sharp, Mirror, Rotate)
- [ ] Advanced Image (Anti-flicker, Exposure, White Balance, DayNight, Backlight, LED light, 3D-NR)
- [ ] Image Data -> "Snap" Frame from Video Stream

SET:
- [ ] Display -> OSD
- [ ] Recording -> Encode (Clear and Fluent Stream)
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
- [X] System -> General
- [ ] System -> DST
- [X] System -> Reboot
- [ ] User -> Online User
- [ ] User -> Add User
- [ ] User -> Manage User
- [ ] Device -> HDD/SD Card
- [ ] Zoom
- [ ] Focus
- [ ] Image (Brightness, Contrass, Saturation, Hue, Sharp, Mirror, Rotate)
- [ ] Advanced Image (Anti-flicker, Exposure, White Balance, DayNight, Backlight, LED light, 3D-NR)
