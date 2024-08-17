# Video review GUI
# https://github.com/sven337/ReolinkLinux/wiki#reolink-video-review-gui

import os
import signal
import sys
import re
import datetime
import subprocess
from configparser import RawConfigParser
from datetime import datetime as dt, timedelta
from reolinkapi import Camera
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QPushButton, QLabel, QFileDialog, QHeaderView, QStyle, QSlider, QStyleOptionSlider, QSplitter
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import Qt, QUrl, QTimer, QThread, pyqtSignal, QMutex, QWaitCondition
from PyQt6.QtGui import QColor, QBrush, QFont, QIcon
from collections import deque

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def path_name_from_camera_path(fname):
   # Mp4Record/2024-08-12/RecM13_DST20240812_214255_214348_1F1E828_4DDA4D.mp4
   return fname.replace('/', '_')

# Function to decode hex values into individual flags
def decode_hex_to_flags(hex_value):
    flags_mapping = {
        'resolution_index': (21, 7), 
        'tv_system': (20, 1),        
        'framerate': (13, 7),        
        'audio_index': (11, 2),      
        'ai_pd': (10, 1),          # person  
        'ai_fd': (9, 1),              # face
        'ai_vd': (8, 1),             # vehicle
        'ai_ad': (7, 1),             # animal
        'encoder_type_index': (5, 2),
        'is_schedule_record': (4, 1), #scheduled
        'is_motion_record': (3, 1),  # motion detected
        'is_rf_record': (2, 1),      
        'is_doorbell_press_record': (1, 1),
        'ai_other': (0, 1)               
    }
    hex_value = int(hex_value, 16)  # Convert hex string to integer
    flag_values = {}
    for flag, (bit_position, bit_size) in flags_mapping.items():
        mask = ((1 << bit_size) - 1) << bit_position
        flag_values[flag] = (hex_value & mask) >> bit_position
    return flag_values

def parse_filename(file_name):
    #  Mp4Record_2024-08-12_RecM13_DST20240812_214255_214348_1F1E828_4DDA4D.mp4
    # https://github.com/sven337/ReolinkLinux/wiki/Figuring-out-the-file-names#file-name-structure
    pattern = r'.*?Mp4Record_(\d{4}-\d{2}-\d{2})_Rec[MS](\d)\d_DST(\d{8})_(\d{6})_(\d{6})_(\w{4,8})_(\w{4,8})\.mp4'
    match = re.match(pattern, file_name)

    if match:
        date = match.group(1)  # YYYY-MM-DD
        channel = int(match.group(2))  # Mx as integer
        start_date = match.group(3)  # YYYYMMDD
        start_time = match.group(4)  # HHMMSS
        end_time = match.group(5)  # HHMMSS
        flags_hex = match.group(6)  # flags hex
        file_size = match.group(7)  # second hexadecimal
        
        # Combine date and start time into a datetime object
        start_datetime = datetime.datetime.strptime(f"{start_date} {start_time}", "%Y%m%d %H%M%S")
        
        triggers = decode_hex_to_flags(flags_hex)
        
        return {'start_datetime': start_datetime, 'channel': channel, 'end_time': end_time, 'triggers': triggers, 'file_size': file_size}
    else:
        print("parse error")
        return None

class ClickableSlider(QSlider):
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            val = self.pixelPosToRangeValue(event.pos())
            self.setValue(val)
        super().mousePressEvent(event)

    def pixelPosToRangeValue(self, pos):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        gr = self.style().subControlRect(QStyle.ComplexControl.CC_Slider, opt, QStyle.SubControl.SC_SliderGroove, self)
        sr = self.style().subControlRect(QStyle.ComplexControl.CC_Slider, opt, QStyle.SubControl.SC_SliderHandle, self)

        if self.orientation() == Qt.Orientation.Horizontal:
            sliderLength = sr.width()
            sliderMin = gr.x()
            sliderMax = gr.right() - sliderLength + 1
            pos = pos.x()
        else:
            sliderLength = sr.height()
            sliderMin = gr.y()
            sliderMax = gr.bottom() - sliderLength + 1
            pos = pos.y()

        return QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), pos - sliderMin, sliderMax - sliderMin, opt.upsideDown)

class DownloadThread(QThread):
    download_complete = pyqtSignal(str)
    download_start = pyqtSignal(str)

    def __init__(self, download_queue, cam):
        super().__init__()
        self.download_queue = download_queue
        self.cam = cam
        self.mutex = QMutex()
        self.wait_condition = QWaitCondition()
        self.is_running = True

    def run(self):
        while self.is_running:
            self.mutex.lock()
            if len(self.download_queue) == 0:
                self.wait_condition.wait(self.mutex)
            self.mutex.unlock()

            if not self.is_running:
                break

            try:
                fname, output_path = self.download_queue.popleft()
                output_path = os.path.join(video_storage_dir, output_path)
                if os.path.isfile(output_path):
                    print(f"File already exists: {output_path}")
                    self.download_complete.emit(output_path)
                else:
                    print(f"Downloading: {fname}")
                    self.download_start.emit(output_path)
                    resp = self.cam.get_file(fname, output_path=output_path)
                    if resp:
                        print(f"Download complete: {output_path}")
                        self.download_complete.emit(output_path)
                    else:
                        print(f"Download failed: {fname}")
            except IndexError:
                pass

    def stop(self):
        self.mutex.lock()
        self.is_running = False
        self.mutex.unlock()
        self.wait_condition.wakeAll()

    def add_to_queue(self, fname, output_path, left=False):
        self.mutex.lock()
        if left:
            self.download_queue.appendleft((fname, output_path))
        else:
            self.download_queue.append((fname, output_path))
        self.wait_condition.wakeOne()
        self.mutex.unlock()


class VideoPlayer(QWidget):
    file_exists_signal = pyqtSignal(str)

    def __init__(self, video_files):
        super().__init__()
        self.setWindowTitle("Reolink Video Review GUI")
        self.cam = cam
        self.download_queue = deque()
        self.download_thread = DownloadThread(self.download_queue, self.cam)
        self.download_thread.download_start.connect(self.on_download_start)
        self.download_thread.download_complete.connect(self.on_download_complete)
        self.download_thread.start()

        # Create media player
        self.media_player = QMediaPlayer()
        self.media_player.errorOccurred.connect(self.handle_media_player_error)

        # Create video widget
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setPlaybackRate(1.5)
        
        # Create table widget to display video files
        self.video_table = QTableWidget()
        self.video_table.setColumnCount(10)
        self.video_table.setHorizontalHeaderLabels(["Status", "Video Path", "Start Datetime", "End Time", "Channel", "Person", "Vehicle", "Pet", "Motion", "Timer" ])
        self.video_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.video_table.setSortingEnabled(True)
        self.video_table.cellClicked.connect(self.play_video)

        # Set smaller default column widths
        self.video_table.setColumnWidth(0, 35)   # Status
        self.video_table.setColumnWidth(1, 120)  # Video Path
        self.video_table.setColumnWidth(2, 130)  # Start Datetime
        self.video_table.setColumnWidth(3, 80)   # End Time
        self.video_table.setColumnWidth(4, 35)   # Channel
        self.video_table.setColumnWidth(5, 35)   # Person
        self.video_table.setColumnWidth(6, 35)   # Vehicle
        self.video_table.setColumnWidth(7, 35)   # Pet
        self.video_table.setColumnWidth(8, 35)   # Motion
        self.video_table.setColumnWidth(9, 30)   # Timer

        self.video_table.verticalHeader().setVisible(False)

        QIcon.setThemeName("Adwaita")

        # Create open button to select video files
        self.open_button = QPushButton("Open Videos")
        self.open_button.clicked.connect(self.open_videos)
        
        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_button.clicked.connect(self.play_pause)

        self.mpv_button = QPushButton("MPV")
        self.mpv_button.clicked.connect(self.open_in_mpv)
        
        # Create seek slider
        self.seek_slider = ClickableSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setRange(0, 0)
        self.seek_slider.sliderPressed.connect(self.seek_slider_pressed)
        self.seek_slider.sliderReleased.connect(self.seek_slider_released)
        self.seek_slider.sliderMoved.connect(self.seek_slider_moved)
        self.media_player.positionChanged.connect(self.update_position)
        self.media_player.durationChanged.connect(self.update_duration)
        
        # Create playback speed slider
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(50, 300)
        self.speed_slider.setValue(200)
        self.speed_slider.valueChanged.connect(self.set_speed)
        speed_label = QLabel("Speed: 2.0x")
        self.speed_slider.valueChanged.connect(lambda v: speed_label.setText(f"Speed: {v/100:.1f}x"))
        
        main_layout = QHBoxLayout()
        # Create a splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side (table and open button)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(self.video_table)
        left_layout.addWidget(self.open_button)
        splitter.addWidget(left_widget)
        
        # Right side (video player and controls)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.addWidget(self.video_widget, 1)

        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)

        control_layout = QHBoxLayout()
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.seek_slider)
        control_layout.addWidget(self.mpv_button)
        controls_layout.addLayout(control_layout)

        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed:"))
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(speed_label)
        controls_layout.addLayout(speed_layout)
        right_layout.addWidget(controls_widget)
        splitter.addWidget(right_widget)
        
        # Set initial sizes
        splitter.setSizes([300, 700]) 
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        self.file_exists_signal.connect(self.on_download_complete)

        self.add_initial_videos(video_files)

    def add_initial_videos(self, video_files):
        for video_path in video_files:
            self.add_video(video_path)
        self.video_table.sortItems(2, Qt.SortOrder.DescendingOrder)

    def open_videos(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilters(["Videos (*.mp4 *.avi *.mov)"])
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles) 
        if file_dialog.exec():
            self.video_table.setSortingEnabled(False)
            for file in file_dialog.selectedFiles():
               self.add_video(os.path.basename(file))
            self.video_table.setSortingEnabled(True)
        self.video_table.sortItems(2, Qt.SortOrder.DescendingOrder)

    def add_video(self, video_path):
        # We are passed the camera file name, e.g. Mp4Record/2024-08-12/RecM13_DST20240812_214255_214348_1F1E828_4DDA4D.mp4
        file_path = path_name_from_camera_path(video_path)  
        base_file_name = file_path
        parsed_data = parse_filename(file_path)
        if parsed_data:
            row_position = self.video_table.rowCount()
            self.video_table.insertRow(row_position)
            start_datetime_str = parsed_data['start_datetime'].strftime("%Y-%m-%d %H:%M:%S")
            start_datetime_item = QTableWidgetItem(start_datetime_str)
            start_datetime_item.setData(Qt.ItemDataRole.UserRole, parsed_data['start_datetime'])
   
            end_time = datetime.datetime.strptime(parsed_data['end_time'], "%H%M%S")
            end_time_str = end_time.strftime("%H:%M:%S")

            # Create the item for the first column with the base file name
            file_name_item = QTableWidgetItem(base_file_name)

            # Set the full path as tooltip
            file_name_item.setToolTip(base_file_name)

            # Set the style for queued status
            grey_color = QColor(200, 200, 200)  # Light grey
            file_name_item.setForeground(QBrush(grey_color))
            font = QFont()
            font.setItalic(True)
            file_name_item.setFont(font)

            status_item = QTableWidgetItem()
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.video_table.setItem(row_position, 0, status_item)
            self.video_table.setItem(row_position, 1, file_name_item)
            self.video_table.setItem(row_position, 2, start_datetime_item)
            self.video_table.setItem(row_position, 3, QTableWidgetItem(end_time_str))
            self.video_table.setItem(row_position, 4, QTableWidgetItem(f"{parsed_data['channel']}"))
            
            # Set individual trigger flags
            self.video_table.setItem(row_position, 5, QTableWidgetItem("✓" if parsed_data['triggers']['ai_pd'] else ""))
            self.video_table.setItem(row_position, 6, QTableWidgetItem("✓" if parsed_data['triggers']['ai_vd'] else ""))
            self.video_table.setItem(row_position, 7, QTableWidgetItem("✓" if parsed_data['triggers']['ai_ad'] else ""))
            self.video_table.setItem(row_position, 8, QTableWidgetItem("✓" if parsed_data['triggers']['is_motion_record'] else ""))
            self.video_table.setItem(row_position, 9, QTableWidgetItem("✓" if parsed_data['triggers']['is_schedule_record'] else ""))

            if parsed_data['triggers']['ai_other']:
                print(f"File {file_path} has ai_other flag!")

            # Make the fields non-editable
            for column in range(self.video_table.columnCount()):
                item = self.video_table.item(row_position, column)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            output_path = os.path.join(video_storage_dir, base_file_name)
            if os.path.isfile(output_path):
                status_item.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
                self.file_exists_signal.emit(output_path)
            else:
                # Add to download queue
                status_item.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_CommandLink))
                self.download_thread.add_to_queue(video_path, base_file_name)
        else:
            print(f"Could not parse file {video_path}")
    
    def on_download_complete(self, video_path):
        for row in range(self.video_table.rowCount()):
            if self.video_table.item(row, 1).text() == os.path.basename(video_path):
                file_name_item = self.video_table.item(row, 1)
                file_name_item.setForeground(QBrush(QColor(0, 0, 0)))  # Black color for normal text
                font = QFont()
                font.setItalic(False)
                font.setBold(False)
                file_name_item.setFont(font)
                status_item = self.video_table.item(row, 0)
                status_item.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
                break
    
    def on_download_start(self, video_path):
        for row in range(self.video_table.rowCount()):
            if self.video_table.item(row, 1).text() == os.path.basename(video_path):
                file_name_item = self.video_table.item(row, 1)
                grey_color = QColor(200, 200, 200)  # Light grey
                file_name_item.setForeground(QBrush(grey_color))
                font = QFont()
                font.setBold(True)
                file_name_item.setFont(font)
                status_item = self.video_table.item(row, 0)
                status_item.setIcon(QIcon.fromTheme("emblem-synchronizing"))
                break

    def play_video(self, row, column):
        file_name_item = self.video_table.item(row, 1)
        video_path = os.path.join(video_storage_dir, file_name_item.text())
       
        if file_name_item.font().italic() or file_name_item.foreground().color().lightness() >= 200:
            print(f"Video {video_path} is not yet downloaded. Moving it to top of queue. Please wait for download.")
             # Find the item in the download_queue that matches the base file name
            found_item = None
            for item in list(self.download_queue):
                if item[1] == file_name_item.text():
                    found_item = item
                    break

            if found_item:
                # Remove the item from its current position in the queue
                self.download_queue.remove(found_item)
                # Add the item to the end of the queue
                self.download_thread.add_to_queue(*found_item, left=True)
            return

        print(f"Playing video: {video_path}")
        url = QUrl.fromLocalFile(video_path)
        self.media_player.setSource(url)
        self.video_widget.show()
        def start_playback():
                # Seek to 5 seconds (pre-record)
                self.media_player.setPosition(5000)
                self.media_player.play()
                self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
                print(f"Media player state: {self.media_player.playbackState()}")

        # Timer needed to be able to play at seek offset in the video, otherwise setPosition seems ignored
        QTimer.singleShot(20, start_playback)

    def play_pause(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        else:
            self.media_player.play()
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))

    def handle_media_player_error(self, error):
        print(f"Media player error: {error}")

    def seek_slider_pressed(self):
        self.media_player.setPosition(self.seek_slider.value())
        self.media_player.play()

    def seek_slider_released(self):
        self.media_player.setPosition(self.seek_slider.value())
        self.media_player.play()

    def seek_slider_moved(self, position):
        # Update video frame while dragging
        self.media_player.setPosition(position)

    def update_position(self, position):
            self.seek_slider.setValue(position)

    def update_duration(self, duration):
        self.seek_slider.setRange(0, duration)

    def set_speed(self, speed):
        self.media_player.setPlaybackRate(speed / 100)

    def open_in_mpv(self):
        current_video = self.media_player.source().toString()
        if current_video:
            # Remove the 'file://' prefix if present
            video_path = current_video.replace('file://', '')
            try:
                subprocess.Popen(['mpv', video_path])
            except FileNotFoundError:
                print("Error: MPV player not found. Make sure it's installed and in your system PATH.")
        else:
            print("No video is currently selected.")

    def closeEvent(self, event):
        self.download_thread.stop()
        self.download_thread.wait()
        super().closeEvent(event)

def read_config(props_path: str) -> dict:
    """Reads in a properties file into variables.

    NB! this config file is kept out of commits with .gitignore. The structure of this file is such:
    # secrets.cfg
        [camera]
        ip={ip_address}
        username={username}
        password={password}
    """
    config = RawConfigParser()
    assert os.path.exists(props_path), f"Path does not exist: {props_path}"
    config.read(props_path)
    return config


def signal_handler(sig, frame):
    print("Exiting the application...")
    sys.exit(0)
    QApplication.quit()



if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
# Read in your ip, username, & password
#   (NB! you'll likely have to create this file. See tests/test_camera.py for details on structure)
    config = read_config('camera.cfg')

    ip = config.get('camera', 'ip')
    un = config.get('camera', 'username')
    pw = config.get('camera', 'password')
    video_storage_dir = config.get('camera', 'video_storage_dir')

# Connect to camera
    cam = Camera(ip, un, pw, https=True)

    start = dt.combine(dt.now(), dt.min.time())
    end = dt.now()
    processed_motions = cam.get_motion_files(start=start, end=end, streamtype='sub', channel=0)
    processed_motions += cam.get_motion_files(start=start, end=end, streamtype='sub', channel=1)

    start = dt.now() - timedelta(days=1)
    end = dt.combine(start, dt.max.time())
    processed_motions += cam.get_motion_files(start=start, end=end, streamtype='sub', channel=0)
    processed_motions += cam.get_motion_files(start=start, end=end, streamtype='sub', channel=1)


    if len(processed_motions) == 0:
        print("Camera did not return any video?!")

    video_files = []
    for i, motion in enumerate(processed_motions):
        fname = motion['filename']
        print("Processing %s" % (fname))
        video_files.append(fname)

    video_files.extend(sys.argv[1:])
    app = QApplication(sys.argv)
    player = VideoPlayer(video_files)
    player.resize(1900, 1000)
    player.show()
    sys.exit(app.exec())
