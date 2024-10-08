import sys
import os
from configparser import RawConfigParser
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSlider
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtGui import QWheelEvent
from reolinkapi import Camera
from threading import Lock

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
        self.setWindowTitle("Reolink PTZ Streamer")
        self.setGeometry(10, 10, 2400, 900)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus) 

        self.camera = camera
        self.zoom_timer = QTimer(self)
        self.zoom_timer.timeout.connect(self.stop_zoom)

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


    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down):
            self.start_move(event.key())

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return
        if event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down):
            self.stop_move()

    def start_move(self, key):
        direction = {
            Qt.Key.Key_Left: "left",
            Qt.Key.Key_Right: "right",
            Qt.Key.Key_Up: "up",
            Qt.Key.Key_Down: "down"
        }.get(key)

        if direction:
            self.move_camera(direction)

    def stop_move(self):
        response = self.camera.stop_ptz()
        print("Stop PTZ")
        if response[0].get('code') != 0:
            self.show_error_message("Failed to stop camera movement", str(response[0]))

    def move_camera(self, direction):
        speed = 25
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
            print(f"Moving camera {direction}")
        else:
            self.show_error_message(f"Failed to move camera {direction}", str(response[0]))

    def handle_wheel_event(self, event: QWheelEvent):
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom_in()
        elif delta < 0:
            self.zoom_out()

    def zoom_in(self):
        self.start_zoom('in')

    def zoom_out(self):
        self.start_zoom('out')

    def start_zoom(self, direction: str):
        self.zoom_timer.stop()  # Stop any ongoing zoom timer
        speed = 60  # You can adjust this value as needed
        if direction == 'in':
            response = self.camera.start_zooming_in(speed)
        else:
            response = self.camera.start_zooming_out(speed)
        
        if response[0].get('code') == 0:
            print(f"Zooming {direction}")
            self.zoom_timer.start(200)  # Stop zooming after 200ms
        else:
            self.show_error_message(f"Failed to start zooming {direction}", str(response[0]))

    def stop_zoom(self):
        response = self.camera.stop_zooming()
        if response[0].get('code') != 0:
            self.show_error_message("Failed to stop zooming", str(response[0]))

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
