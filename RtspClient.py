import socket

import cv2
import numpy
import socks


class RtspClient:

    def __init__(self, ip, username, password, port=554, profile="main", **kwargs):
        """

        :param ip:
        :param username:
        :param password:
        :param port: rtsp port
        :param profile: "main" or "sub"
        :param proxies: {"host": "localhost", "port": 8000}
        """
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        self.sockt = None
        self.url = "rtsp://" + self.username + ":" + self.password + "@" + self.ip + ":" + str(
            self.port) + "//h264Preview_01_" + profile
        self.proxy = kwargs.get("proxies")

    def __enter__(self):
        self.sockt = self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sockt.close()

    def connect(self) -> socket:
        try:
            sockt = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
            sockt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if self.proxy is not None:
                sockt.set_proxy(socks.SOCKS5, self.proxy["host"], self.proxy["port"])
            sockt.connect((self.ip, self.port))
            return sockt
        except Exception as e:
            print(e)

    def get_frame(self) -> bytearray:
        try:
            self.sockt.send(str.encode(self.url))
            data = b''
            while True:
                try:
                    r = self.sockt.recv(90456)
                    if len(r) == 0:
                        break
                    a = r.find(b'END!')
                    if a != -1:
                        data += r[:a]
                        break
                    data += r
                except Exception as e:
                    print(e)
                    continue
            nparr = numpy.fromstring(data, numpy.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return frame
        except Exception as e:
            print(e)

    def preview(self):
        """ Blocking function. Opens OpenCV window to display stream. """
        self.connect()
        win_name = 'RTSP'
        cv2.namedWindow(win_name, cv2.WINDOW_AUTOSIZE)
        cv2.moveWindow(win_name, 20, 20)

        while True:
            cv2.imshow(win_name, self.get_frame())
            # if self._latest is not None:
            #    cv2.imshow(win_name,self._latest)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        cv2.waitKey()
        cv2.destroyAllWindows()
        cv2.waitKey()
