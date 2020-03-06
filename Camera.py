from api import APIHandler


class Camera(APIHandler):

    def __init__(self, ip, username="admin", password="", https=False):
        """
        Initialise the Camera object by passing the ip address.
        The default details {"username":"admin", "password":""} will be used if nothing passed
        :param ip:
        :param username:
        :param password:
        """
        # For when you need to connect to a camera behind a proxy, pass
        # a proxy argument: proxy={"http": "socks5://127.0.0.1:8000"}
        APIHandler.__init__(self, ip, username, password, https=https)

        # Normal call without proxy:
        # APIHandler.__init__(self, ip, username, password)

        self.ip = ip
        self.username = username
        self.password = password
        super().login()
