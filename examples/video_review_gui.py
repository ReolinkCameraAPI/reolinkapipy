# Video review GUI
# https://github.com/sven337/ReolinkLinux/wiki#reolink-video-review-gui

import os
import signal
import sys
import re
import datetime
import subprocess
import argparse
from configparser import RawConfigParser
from datetime import datetime as dt, timedelta
from reolinkapi import Camera
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QPushButton, QLabel, QFileDialog, QHeaderView, QStyle, QSlider, QStyleOptionSlider, QSplitter, QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator
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
    #  Mp4Record_2024-09-13-RecS09_DST20240907_084519_084612_0_55289080000000_307BC0.mp4
    # https://github.com/sven337/ReolinkLinux/wiki/Figuring-out-the-file-names#file-name-structure
    pattern = r'.*?Mp4Record_(\d{4}-\d{2}-\d{2})_Rec[MS](\d)(\d)_(DST)?(\d{8})_(\d{6})_(\d{6})'
    v3_suffix = r'.*_(\w{4,8})_(\w{4,8})\.mp4'
    v9_suffix = r'.*_(\d)_(\w{7})(\w{7})_(\w{4,8})\.mp4'
    match = re.match(pattern, file_name)

    out = {}
    version = 0

    if match:
        date = match.group(1)  # YYYY-MM-DD
        channel = int(match.group(2))  
        version = int(match.group(3)) # version
        start_date = match.group(5)  # YYYYMMDD
        start_time = match.group(6)  # HHMMSS
        end_time = match.group(7)  # HHMMSS

        # Combine date and start time into a datetime object
        start_datetime = datetime.datetime.strptime(f"{start_date} {start_time}", "%Y%m%d %H%M%S")
        
        out = {'start_datetime': start_datetime, 'channel': channel, 'end_time': end_time }
    else:
        print("parse error")
        return None
       
    if version == 9:
        match = re.match(v9_suffix, file_name)
        if not match:
            print(f"v9 parse error for {file_name}")
            return None

        animal_type = match.group(1)
        flags_hex1 = match.group(2)
        flags_hex2 = match.group(3)
        file_size = int(match.group(4), 16)

        triggers = decode_hex_to_flags(flags_hex1)

        out.update({'animal_type' : animal_type, 'file_size' : file_size, 'triggers' : triggers })

    elif version == 2 or version == 3:
        match = re.match(v3_suffix, file_name)
        if not match:
            print(f"v3 parse error for {file_name}")
            return None

        flags_hex = match.group(1)
        file_size = int(match.group(2), 16)

        triggers = decode_hex_to_flags(flags_hex)

        out.update({'file_size' : file_size, 'triggers' : triggers })

    return out

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
    download_complete = pyqtSignal(str, bool)
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
                print(f"Downloading: {fname}")
                self.download_start.emit(output_path)
                resp = self.cam.get_file(fname, output_path=output_path)
                if resp:
                    print(f"Download complete: {output_path}")
                    self.download_complete.emit(output_path, True)
                else:
                    print(f"Download failed: {fname}")
                    self.download_complete.emit(output_path, False)
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
    file_exists_signal = pyqtSignal(str, bool)

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
        self.video_tree = QTreeWidget()
        self.video_tree.setColumnCount(10)
        self.video_tree.setHeaderLabels(["Status", "Video Path", "Start Datetime", "End Time", "Channel", "Person", "Vehicle", "Pet", "Motion", "Timer"])
        self.video_tree.setSortingEnabled(True)
        self.video_tree.itemClicked.connect(self.play_video)

        # Set smaller default column widths
        self.video_tree.setColumnWidth(0, 35)   # Status
        self.video_tree.setColumnWidth(1, 120)  # Video Path
        self.video_tree.setColumnWidth(2, 130)  # Start Datetime
        self.video_tree.setColumnWidth(3, 70)   # End Time
        self.video_tree.setColumnWidth(4, 35)   # Channel
        self.video_tree.setColumnWidth(5, 35)   # Person
        self.video_tree.setColumnWidth(6, 35)   # Vehicle
        self.video_tree.setColumnWidth(7, 35)   # Pet
        self.video_tree.setColumnWidth(8, 35)   # Motion
        self.video_tree.setColumnWidth(9, 30)   # Timer

        self.video_tree.setIndentation(10)

        QIcon.setThemeName("Adwaita")

        # Create open button to select video files
        self.open_button = QPushButton("Open Videos")
        self.open_button.clicked.connect(self.open_videos)
        
        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_button.clicked.connect(self.play_pause)

        self.mpv_button = QPushButton("MPV")
        self.mpv_button.clicked.connect(self.open_in_mpv)
       
        self.get_highres_button = QPushButton("GetHighRes")
        self.get_highres_button.clicked.connect(self.get_highres_stream_for_file)
        self.get_highres_button.setEnabled(False)  # Disable by default

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
        left_layout.addWidget(self.video_tree)
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
        control_layout.addWidget(self.get_highres_button)
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
        self.video_tree.sortItems(2, Qt.SortOrder.DescendingOrder)
#        self.video_tree.expandAll()

    def open_videos(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilters(["Videos (*.mp4 *.avi *.mov)"])
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles) 
        if file_dialog.exec():
            self.video_tree.setSortingEnabled(False)
            for file in file_dialog.selectedFiles():
               self.add_video(os.path.basename(file))
            self.video_tree.setSortingEnabled(True)
        self.video_tree.sortItems(2, Qt.SortOrder.DescendingOrder)
#        self.video_tree.expandAll()

    def add_video(self, video_path):
        # We are passed the camera file name, e.g. Mp4Record/2024-08-12/RecM13_DST20240812_214255_214348_1F1E828_4DDA4D.mp4
        file_path = path_name_from_camera_path(video_path)  
        base_file_name = file_path
        parsed_data = parse_filename(file_path)
        if not parsed_data:
            print(f"Could not parse file {video_path}")
            return

        start_datetime = parsed_data['start_datetime']
        channel = parsed_data['channel']

        end_time = datetime.datetime.strptime(parsed_data['end_time'], "%H%M%S")
        end_time_str = end_time.strftime("%H:%M:%S")

        video_item = QTreeWidgetItem()
        video_item.setText(0, "") # Status
        video_item.setTextAlignment(0, Qt.AlignmentFlag.AlignCenter)
        video_item.setText(1, base_file_name)
        video_item.setText(2, start_datetime.strftime("%Y-%m-%d %H:%M:%S"))
        video_item.setData(2, Qt.ItemDataRole.UserRole, parsed_data['start_datetime'])
        video_item.setText(3, end_time_str)
        video_item.setText(4, str(channel))
        video_item.setText(5, "✓" if parsed_data['triggers']['ai_pd'] else "")
        video_item.setText(6, "✓" if parsed_data['triggers']['ai_vd'] else "")
        video_item.setText(7, "✓" if parsed_data['triggers']['ai_ad'] else "")
        video_item.setText(8, "✓" if parsed_data['triggers']['is_motion_record'] else "")
        video_item.setText(9, "✓" if parsed_data['triggers']['is_schedule_record'] else "")

        if parsed_data['triggers']['ai_other']:
            print(f"File {file_path} has ai_other flag!")
        
        video_item.setToolTip(1, base_file_name)
        # Set the style for queued status
        grey_color = QColor(200, 200, 200)  # Light grey
        video_item.setForeground(1, QBrush(grey_color))
        font = QFont()
        font.setItalic(True)
        video_item.setFont(1, font)

        # Make the fields non-editable
        iterator = QTreeWidgetItemIterator(self.video_tree)
        while iterator.value():
            item = iterator.value()
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            iterator += 1

        # Find a potentially pre-existing channel0 item for this datetime, if so, add as a child
        # This lets channel1 appear as a child, but also main & sub videos appear in the same group
        channel_0_item = self.find_channel_0_item(start_datetime)
        if channel_0_item:
            channel_0_item.addChild(video_item)
        else:
            self.video_tree.addTopLevelItem(video_item)

        output_path = os.path.join(video_storage_dir, base_file_name)
        expected_size = parsed_data['file_size']

        need_download = True
        if os.path.isfile(output_path):
            actual_size = os.path.getsize(output_path)
            if actual_size == expected_size:
                need_download = False
                self.file_exists_signal.emit(output_path, True)
            else:
                print(f"File size mismatch for {output_path}. Expected: {expected_size}, Actual: {actual_size}. Downloading again")
        
        if need_download:
            video_item.setIcon(1, self.style().standardIcon(QStyle.StandardPixmap.SP_CommandLink))
            self.download_thread.add_to_queue(video_path, base_file_name)

    def find_channel_0_item(self, datetime_obj):
        # Truncate seconds to nearest 10
        truncated_seconds = datetime_obj.second - (datetime_obj.second % 10)
        truncated_datetime = datetime_obj.replace(second=truncated_seconds)
        
        for i in range(self.video_tree.topLevelItemCount()):
            item = self.video_tree.topLevelItem(i)
            item_datetime = item.data(2, Qt.ItemDataRole.UserRole)
            item_truncated = item_datetime.replace(second=item_datetime.second - (item_datetime.second % 10))
            if item_truncated == truncated_datetime:
                return item
        return None

    def find_item_by_path(self, path):
        iterator = QTreeWidgetItemIterator(self.video_tree)
        while iterator.value():
            item = iterator.value()
            text = item.text(1)
            if text == path:
                return item
            iterator += 1
        print(f"Could not find item by path {path}")
        return None

    def on_download_complete(self, video_path, success):
        item = self.find_item_by_path(os.path.basename(video_path))
        if not item:
            print(f"on_download_complete {video_path} did not find item?!")
        item.setForeground(1, QBrush(QColor(0, 0, 0)))  # Black color for normal text
        font = item.font(1)
        font.setItalic(False)
        font.setBold(False)
        item.setFont(1, font)
        if success:
            if "RecS" in item.text(1):
                # One day (hopefully) offer the option to download the
                # high-res version This is not trivial because we have to
                # re-do a camera search for the relevant time period and
                # match based on start and end dates (+/- one second in my
                # experience)
                # For now simply display that this is low-res.
                item.setText(0, "sub")
            item.setIcon(1, QIcon())
        else:
            item.setIcon(1, self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical))


    def on_download_start(self, video_path):
        item = self.find_item_by_path(os.path.basename(video_path))
        if item:
            grey_color = QColor(200, 200, 200)  # Light grey
            item.setForeground(1, QBrush(grey_color))
            font = item.font(1)
            font.setBold(True)
            item.setFont(1, font)
            item.setIcon(1, QIcon.fromTheme("emblem-synchronizing"))
        else:
            print(f"Cannot find item for {video_path}")

    def play_video(self, file_name_item, column):
        video_path = os.path.join(video_storage_dir, file_name_item.text(1))
       
        if file_name_item.font(1).italic() or file_name_item.foreground(1).color().lightness() >= 200:
            print(f"Video {video_path} is not yet downloaded. Moving it to top of queue. Please wait for download.")
             # Find the item in the download_queue that matches the base file name
            found_item = None
            for item in list(self.download_queue):
                if item[1] == file_name_item.text(1):
                    found_item = item
                    break

            if found_item:
                # Remove the item from its current position in the queue
                self.download_queue.remove(found_item)
                # Add the item to the end of the queue
                self.download_thread.add_to_queue(*found_item, left=True)
            return

        # Enable/disable GetHighRes button based on whether it's a sub stream
        self.get_highres_button.setEnabled("RecS" in file_name_item.text(1))

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

    def get_highres_stream_for_file(self):
        current_item = self.video_tree.currentItem()
        if not current_item or "RecS" not in current_item.text(1):
            return

        parsed_data = parse_filename(current_item.text(1))
        if not parsed_data:
            print(f"Could not parse file {current_item.text(1)}")
            return

        start_time = parsed_data['start_datetime'] - timedelta(seconds=1)
        end_time = datetime.datetime.strptime(f"{parsed_data['start_datetime'].strftime('%Y%m%d')} {parsed_data['end_time']}", "%Y%m%d %H%M%S") + timedelta(seconds=1)

        main_files = self.cam.get_motion_files(start=start_time, end=end_time, streamtype='main', channel=parsed_data['channel'])

        if main_files:
            for main_file in main_files:
                self.add_video(main_file['filename'])
            self.video_tree.sortItems(2, Qt.SortOrder.DescendingOrder)
        else:
            print(f"No main stream file found for {current_item.text(1)}")

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
        self.download_thread.wait(1000)
        self.download_thread.terminate()
        self.cam.logout()
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
    cam.logout()
    QApplication.quit()



if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    
    parser = argparse.ArgumentParser(description="Reolink Video Review GUI")
    parser.add_argument('--sub', action='store_true', help="Search for sub channel instead of main channel")
    parser.add_argument('files', nargs='*', help="Optional video file names to process")
    args = parser.parse_args()

    config = read_config('camera.cfg')

    ip = config.get('camera', 'ip')
    un = config.get('camera', 'username')
    pw = config.get('camera', 'password')
    video_storage_dir = config.get('camera', 'video_storage_dir')

# Connect to camera
    cam = Camera(ip, un, pw, https=True)

    start = dt.combine(dt.now(), dt.min.time())
    end = dt.now()

    streamtype = 'sub' if args.sub else 'main'
    processed_motions = cam.get_motion_files(start=start, end=end, streamtype=streamtype, channel=0)
    processed_motions += cam.get_motion_files(start=start, end=end, streamtype=streamtype, channel=1)

    start = dt.now() - timedelta(days=1)
    end = dt.combine(start, dt.max.time())
    processed_motions += cam.get_motion_files(start=start, end=end, streamtype=streamtype, channel=0)
    processed_motions += cam.get_motion_files(start=start, end=end, streamtype=streamtype, channel=1)


    if len(processed_motions) == 0:
        print("Camera did not return any video?!")

    video_files = []
    for i, motion in enumerate(processed_motions):
        fname = motion['filename']
        print("Processing %s" % (fname))
        video_files.append(fname)

    video_files.extend([os.path.basename(file) for file in args.files])
    app = QApplication(sys.argv)
    player = VideoPlayer(video_files)
    player.resize(2400, 1000)
    player.show()
    sys.exit(app.exec())
