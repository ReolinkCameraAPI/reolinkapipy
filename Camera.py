from APIHandler import APIHandler


class Camera(APIHandler):

    def __init__(self, ip, username="admin", password=""):
        APIHandler.__init__(self, ip)
        self.ip = ip
        self.username = username
        self.password = password
        super().login(self.username, self.password)
