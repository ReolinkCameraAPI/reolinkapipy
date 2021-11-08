from reolinkapi.handlers.api_handler import APIHandler


class Camera(APIHandler):

    def __init__(self, ip: str,
                 username: str = "admin",
                 password: str = "",
                 https: bool = False,
                 defer_login: bool = False,
                 profile: str = "main",
                 **kwargs):
        """
        Initialise the Camera object by passing the ip address.
        The default details {"username":"admin", "password":""} will be used if nothing passed
        For deferring the login to the camera, just pass defer_login = True.
        For connecting to the camera behind a proxy pass a proxy argument: proxy={"http": "socks5://127.0.0.1:8000"}
        :param ip:
        :param username:
        :param password:
        :param https: connect to the camera over https
        :param defer_login: defer the login process
        :param proxy: Add a proxy dict for requests to consume.
        eg: {"http":"socks5://[username]:[password]@[host]:[port], "https": ...}
        More information on proxies in requests: https://stackoverflow.com/a/15661226/9313679
        """
        if profile not in ["main", "sub"]:
            raise Exception("Profile argument must be either \"main\" or \"sub\"")

        # For when you need to connect to a camera behind a proxy, pass
        # a proxy argument: proxy={"http": "socks5://127.0.0.1:8000"}
        APIHandler.__init__(self, ip, username, password, https=https, **kwargs)

        # Normal call without proxy:
        # APIHandler.__init__(self, ip, username, password)

        self.ip = ip
        self.username = username
        self.password = password
        self.profile = profile

        if not defer_login:
            super().login()
