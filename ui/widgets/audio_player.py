from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QSlider, QLabel, QFrame
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal, pyqtSlot, QTimer
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtGui import QPainter, QColor, QPainterPath
import numpy as np

class AudioVisualizerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(60)
        self.bars = 20  # Number of frequency bars
        self.bar_values = np.zeros(self.bars)
        self.setStyleSheet("background-color: transparent;")

    def update_values(self, value):
        # Simulate frequency data from audio level
        # In a real implementation, you'd use proper audio analysis
        target = np.random.normal(value, 0.2, self.bars)
        target = np.clip(target, 0, 1)
        # Smooth transition
        self.bar_values = self.bar_values * 0.7 + target * 0.3
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate bar width and spacing
        width = self.width()
        height = self.height()
        bar_width = width / (self.bars * 2)
        spacing = bar_width

        # Draw bars
        for i, value in enumerate(self.bar_values):
            x = i * (bar_width + spacing)
            bar_height = value * height

            # Create gradient
            gradient = QColor(108, 92, 231)  # Primary color
            gradient.setAlpha(int(255 * value))

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(gradient)

            # Draw rounded bar
            path = QPainterPath()
            path.addRoundedRect(
                x, height - bar_height,
                bar_width, bar_height,
                bar_width/2, bar_width/2
            )
            painter.drawPath(path)

            # Mirror bar (optional)
            path = QPainterPath()
            path.addRoundedRect(
                width - x - bar_width, height - bar_height,
                bar_width, bar_height,
                bar_width/2, bar_width/2
            )
            painter.drawPath(path)

class AudioPlayerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_player()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Create frames for styling
        self.player_frame = QFrame()
        self.player_frame.setObjectName("audioPlayerFrame")
        player_layout = QVBoxLayout(self.player_frame)

        # Controls layout
        controls_layout = QHBoxLayout()

        # Play/Pause button
        self.play_button = QPushButton("▶")
        self.play_button.setFixedSize(40, 40)
        self.play_button.setObjectName("playButton")

        # Time labels and slider
        self.time_label = QLabel("0:00")
        self.duration_label = QLabel("0:00")
        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setObjectName("timeSlider")

        # Volume control
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.setValue(100)
        self.volume_slider.setObjectName("volumeSlider")

        # Add visualizer
        self.visualizer = AudioVisualizerWidget()

        # Add widgets to controls layout
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.time_label)
        controls_layout.addWidget(self.time_slider)
        controls_layout.addWidget(self.duration_label)
        controls_layout.addWidget(self.volume_slider)

        # Add everything to main layout
        player_layout.addWidget(self.visualizer)
        player_layout.addLayout(controls_layout)

        layout.addWidget(self.player_frame)

    def setup_player(self):
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        # Connect signals
        self.play_button.clicked.connect(self.toggle_playback)
        self.time_slider.sliderMoved.connect(self.seek)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.player.positionChanged.connect(self.position_changed)
        self.player.durationChanged.connect(self.duration_changed)

        # Setup visualization update timer
        self.viz_timer = QTimer()
        self.viz_timer.timeout.connect(self.update_visualization)
        self.viz_timer.start(16)  # ~60 FPS

    def set_media(self, file_path):
        self.player.setSource(QUrl.fromLocalFile(file_path))
        self.play_button.setText("▶")
        self.audio_output.setVolume(self.volume_slider.value() / 100)

    def toggle_playback(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.play_button.setText("▶")
        else:
            self.player.play()
            self.play_button.setText("⏸")

    def seek(self, position):
        self.player.setPosition(position)

    def set_volume(self, volume):
        self.audio_output.setVolume(volume / 100)

    def position_changed(self, position):
        self.time_slider.setValue(position)
        self.time_label.setText(self.format_time(position))

    def duration_changed(self, duration):
        self.time_slider.setRange(0, duration)
        self.duration_label.setText(self.format_time(duration))

    def format_time(self, ms):
        s = round(ms / 1000)
        m, s = divmod(s, 60)
        return f"{m}:{s:02d}"

    def update_visualization(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            # Get current volume level as basic audio visualization
            level = self.audio_output.volume()
            self.visualizer.update_values(level)
        else:
            self.visualizer.update_values(0)

    def stop(self):
        self.player.stop()
        self.play_button.setText("▶")
