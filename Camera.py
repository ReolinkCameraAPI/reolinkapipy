from APIHandler import APIHandler


class Camera(APIHandler):

    def __init__(self, ip, username="admin", password="", https=False):
        APIHandler.__init__(self, ip, https=https)
        self.ip = ip
        self.username = username
        self.password = password
        self.https = https
        super().login(self.username, self.password)
