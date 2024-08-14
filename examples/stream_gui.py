import sys
import os
from configparser import RawConfigParser
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSlider
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import Qt, QUrl
from reolinkapi import Camera

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
    def __init__(self, rtsp_url, camera: Camera):
        super().__init__()
        self.setWindowTitle("Camera Player")
        self.setGeometry(10, 10, 1900, 1150)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus) 

        self.camera = camera

        # Create media player
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.errorOccurred.connect(self.handle_error)
        self.media_player.setSource(QUrl(rtsp_url))

        # Create video widget
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)

        # Create zoom slider
        self.zoom_slider = ZoomSlider(Qt.Orientation.Vertical)
        self.zoom_slider.setRange(0, 100)
        self.zoom_slider.setValue(0)
        self.zoom_slider.valueChanged.connect(self.set_zoom)

        # Create layout
        layout = QVBoxLayout()
        video_layout = QHBoxLayout()
        video_layout.addWidget(self.video_widget, 4)
        video_layout.addWidget(self.zoom_slider, 1)
        layout.addLayout(video_layout)
        self.setLayout(layout)

        # Set source and start playing
        self.media_player.setSource(QUrl(rtsp_url))
        self.media_player.play()


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
        speed = 25  # You can adjust this value as needed
        try:
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

            response = response[0]
            if response.get('code') == 0:
                print(f"Successfully moved camera {direction}")
            else:
                self.show_error_message(f"Failed to move camera {direction}", response.get('msg', 'Unknown error'))
        except Exception as e:
            self.show_error_message(f"Error moving camera {direction}", str(e))

    def set_zoom(self, value):
        try:
            zoom_speed = value / 2  # Adjust this factor as needed
            if value > self.zoom_slider.value():
                response = self.camera._send_operation('ZoomInc', speed=zoom_speed)
            else:
                response = self.camera._send_operation('ZoomDec', speed=zoom_speed)

            if response.get('code') == 0:
                print(f"Successfully set zoom to {value}")
            else:
                self.show_error_message("Failed to set zoom", response.get('msg', 'Unknown error'))
        except Exception as e:
            self.show_error_message("Error setting zoom", str(e))

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

    rtsp_url = f"rtsp://{un}:{pw}@{ip}/h264Preview_01_sub"

    app = QApplication(sys.argv)
    player = CameraPlayer(rtsp_url, cam)
    player.show()
    sys.exit(app.exec())
