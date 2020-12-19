import os
from threading import ThreadError
from typing import Any
import cv2
from reolinkapi.utils.util import threaded


class RtspClient:
    """
    This is a wrapper of the OpenCV VideoCapture method
    Inspiration from:
        - https://benhowell.github.io/guide/2015/03/09/opencv-and-web-cam-streaming
        - https://stackoverflow.com/questions/19846332/python-threading-inside-a-class
        - https://stackoverflow.com/questions/55828451/video-streaming-from-ip-camera-in-python-using-opencv-cv2-videocapture
    """

    def __init__(self, ip: str, username: str, password: str, port: float = 554, profile: str = "main",
                 use_udp: bool = True, callback: Any = None, **kwargs):
        """
        RTSP client is used to retrieve frames from the camera in a stream

        :param ip: Camera IP
        :param username: Camera Username
        :param password: Camera User Password
        :param port: RTSP port
        :param profile: "main" or "sub"
        :param use_upd: True to use UDP, False to use TCP
        :param proxies: {"host": "localhost", "port": 8000}
        """
        self.capture = None
        self.thread_cancelled = False
        self.callback = callback

        capture_options = 'rtsp_transport;'
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        self.proxy = kwargs.get("proxies")
        self.url = f'rtsp://{self.username}:{self.password}@{self.ip}:{self.port}//h264Preview_01_{profile}'
        capture_options += 'udp' if use_udp else 'tcp'

        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = capture_options

        # opens the stream capture, but does not retrieve any frames yet.
        self._open_video_capture()

    def _open_video_capture(self):
        # To CAP_FFMPEG or not To ?
        self.capture = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)

    def _stream_blocking(self):
        while True:
            try:
                if self.capture.isOpened():
                    ret, frame = self.capture.read()
                    if ret:
                        yield frame
                else:
                    print("stream closed")
                    self.capture.release()
                    return
            except Exception as e:
                print(e)
                self.capture.release()
                return

    @threaded
    def _stream_non_blocking(self):
        while not self.thread_cancelled:
            try:
                if self.capture.isOpened():
                    ret, frame = self.capture.read()
                    if ret:
                        self.callback(frame)
                else:
                    print("stream is closed")
                    self.stop_stream()
            except ThreadError as e:
                print(e)
                self.stop_stream()

    def stop_stream(self):
        self.capture.release()
        self.thread_cancelled = True

    def open_stream(self):
        """
        Opens OpenCV Video stream and returns the result according to the OpenCV documentation
        https://docs.opencv.org/3.4/d8/dfe/classcv_1_1VideoCapture.html#a473055e77dd7faa4d26d686226b292c1
        """

        # Reset the capture object
        if self.capture is None or not self.capture.isOpened():
            self._open_video_capture()

        print("opening stream")

        if self.callback is None:
            return self._stream_blocking()
        else:
            # reset the thread status if the object was not re-created
            if not self.thread_cancelled:
                self.thread_cancelled = False
            return self._stream_non_blocking()
