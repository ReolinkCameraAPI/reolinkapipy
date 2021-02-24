import reolinkapi

if __name__ == "__main__":
    # create a single camera
    # defer_login is optional, if nothing is passed it will attempt to log in.
    cam = reolinkapi.Camera("192.168.0.102", defer_login=True)

    # must first login since I defer have deferred the login process
    cam.login()

    # can now use the camera api
    dst = cam.get_dst()
    ok = cam.add_user("foo", "bar", "admin")
    alarm = cam.get_alarm_motion()

    # discover cameras on the network
    discovery = reolinkapi.Discover()

    # can use upnp
    devices = discovery.discover_upnp()

    # or port scanning using default ports (can set this when setting up Discover object
    devices = discovery.discover_port()

    # create a camera factory, these will authenticate every camera with the same username and password
    factory = reolinkapi.CameraFactory(username="foo", password="bar")

    # create your camera factory, can immediately return the cameras or just keep it inside the factory
    _ = factory.get_cameras_from_devices(devices=devices)

    # initialise the cameras (log them in)
    factory.initialise_cameras()

    # one can check if the camera is authenticated with it's `is_loggedin` property
    for camera in factory.cameras:
        if camera.is_loggedin:
            print(f'camera {camera.ip} is logged in')
        else:
            print(f'camera {camera.ip} is not logged in')
