import sys
import os
from configparser import RawConfigParser
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSlider
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QWheelEvent
from reolinkapi import Camera
from threading import Lock


def read_config(props_path: str) -> dict:
    config = RawConfigParser()
    assert os.path.exists(props_path), f"Path does not exist: {props_path}"
    config.read(props_path)
    return config

class ZoomSlider(QSlider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down):
            event.ignore()
        else:
            super().keyPressEvent(event)

class CameraPlayer(QWidget):
    def __init__(self, rtsp_url_wide, rtsp_url_telephoto, camera: Camera):
        super().__init__()
        self.setWindowTitle("Camera Player")
        self.setGeometry(10, 10, 1900, 1150)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus) 

        self.camera = camera
        self.move_lock = Lock()
        self.move_in_progress = False

        # Create media players
        self.media_player_wide = QMediaPlayer()
        self.media_player_telephoto = QMediaPlayer()

        # Create video widgets
        self.video_widget_wide = QVideoWidget()
        self.video_widget_telephoto = QVideoWidget()
        self.media_player_wide.setVideoOutput(self.video_widget_wide)
        self.media_player_telephoto.setVideoOutput(self.video_widget_telephoto)
        self.video_widget_wide.wheelEvent = self.handle_wheel_event
        self.video_widget_telephoto.wheelEvent = self.handle_wheel_event

        # Create layout
        layout = QHBoxLayout()
        layout.addWidget(self.video_widget_wide, 2)
        layout.addWidget(self.video_widget_telephoto, 2)
        self.setLayout(layout)

        # Start playing the streams
        self.media_player_wide.setSource(QUrl(rtsp_url_wide))
        self.media_player_telephoto.setSource(QUrl(rtsp_url_telephoto))
        self.media_player_wide.play()
        self.media_player_telephoto.play()

    def is_move_in_progress(self):
        with self.move_lock:
            return self.move_in_progress

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_Left:
            self.move_camera("left")
        elif event.key() == Qt.Key.Key_Right:
            self.move_camera("right")
        elif event.key() == Qt.Key.Key_Up:
            self.move_camera("up")
        elif event.key() == Qt.Key.Key_Down:
            self.move_camera("down")

    def move_camera(self, direction):
        if self.is_move_in_progress():
            print(f"Move already in progress, ignoring {direction} command")
            return

        speed = 25
        try:
            with self.move_lock:
                self.move_in_progress = True

            if direction == "left":
                response = self.camera.move_left(speed)
            elif direction == "right":
                response = self.camera.move_right(speed)
            elif direction == "up":
                response = self.camera.move_up(speed)
            elif direction == "down":
                response = self.camera.move_down(speed)
            else:
                print(f"Invalid direction: {direction}")
                return

            if response[0].get('code') == 0:
                print(f"Successfully started moving camera {direction}")
            else:
                self.show_error_message(f"Failed to move camera {direction}", response[0].get('msg', 'Unknown error'))

            # Immediately stop the camera movement
            stop_response = self.camera.stop_ptz()
            if stop_response[0].get('code') != 0:
                self.show_error_message("Failed to stop camera movement", stop_response[0].get('msg', 'Unknown error'))

        except Exception as e:
            self.show_error_message(f"Error moving camera {direction}", str(e))
        finally:
            with self.move_lock:
                self.move_in_progress = False

    def handle_wheel_event(self, event: QWheelEvent):
        delta = event.angleDelta().y()
        if delta > 0:
            self.change_zoom(zoom_in = True)
        elif delta < 0:
            self.change_zoom(zoom_in = False)

    def change_zoom(self, zoom_in):
        zoom_speed = 10
        cmd = 'ZoomInc' if zoom_in else 'ZoomDec'
        response = self.camera._send_operation(cmd, speed=zoom_speed)
        response = response[0]
        print(str(response))

    def show_error_message(self, title, message):
        print(f"Error: {title} {message}")

    def handle_error(self, error):
        print(f"Media player error: {error}")


if __name__ == '__main__':
    # Read in your ip, username, & password from the configuration file
    config = read_config('camera.cfg')
    ip = config.get('camera', 'ip')
    un = config.get('camera', 'username')
    pw = config.get('camera', 'password')

    # Connect to camera
    cam = Camera(ip, un, pw, https=True)

    rtsp_url_wide =      f"rtsp://{un}:{pw}@{ip}/Preview_01_sub"
    rtsp_url_telephoto = f"rtsp://{un}:{pw}@{ip}/Preview_02_sub"

    # Connect to camera
    cam = Camera(ip, un, pw, https=True)

    app = QApplication(sys.argv)
    player = CameraPlayer(rtsp_url_wide, rtsp_url_telephoto, cam)
    player.show()
    sys.exit(app.exec())
