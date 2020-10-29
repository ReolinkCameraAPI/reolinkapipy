import os
import cv2


class RtspClient:

    def __init__(self, ip, username, password, port=554, profile="main", use_udp=True, **kwargs):
        """

        :param ip: Camera IP
        :param username: Camera Username
        :param password: Camera User Password
        :param port: RTSP port
        :param profile: "main" or "sub"
        :param use_upd: True to use UDP, False to use TCP
        :param proxies: {"host": "localhost", "port": 8000}
        """
        capture_options = 'rtsp_transport;'
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        self.proxy = kwargs.get("proxies")
        self.url = "rtsp://" + self.username + ":" + self.password + "@" + \
            self.ip + ":" + str(self.port) + "//h264Preview_01_" + profile
        if use_udp:
            capture_options = capture_options + 'udp'
        else:
            capture_options = capture_options + 'tcp'

        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = capture_options

    def preview(self):
        """ Blocking function. Opens OpenCV window to display stream. """
        win_name = self.ip
        cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
        ret, frame = cap.read()

        while ret:
            cv2.imshow(win_name, frame)

            ret, frame = cap.read()
            if (cv2.waitKey(1) & 0xFF == ord('q')):
                break

        cap.release()
        cv2.destroyAllWindows()
