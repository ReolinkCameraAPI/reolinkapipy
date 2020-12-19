import reolinkapi

if __name__ == "__main__":
    cam = reolinkapi.Camera("192.168.0.102", defer_login=True)

    # must first login since I defer have deferred the login process
    cam.login()

    dst = cam.get_dst()
    ok = cam.add_user("foo", "bar", "admin")
    alarm = cam.get_alarm_motion()
