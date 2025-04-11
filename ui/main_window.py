import sys
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QComboBox, QSlider, QPushButton, QLabel,
    QFrame, QGridLayout, QSpacerItem, QSizePolicy, QFileDialog,
    QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt, QUrl, pyqtSlot
from PyQt6.QtGui import QIcon, QFontDatabase

from .widgets.animated_background import AnimatedBackground
from .widgets.audio_player import AudioPlayerWidget
from .widgets.history_list import HistoryListWidget
from .threads import TTSWorker, VoicesWorker, AudioProcessorWorker, ThemeSwitcherWorker # Added ThemeSwitcherWorker


class MainWindow(QMainWindow):
    def __init__(self, tts_manager, asset_manager):
        super().__init__()
        self.tts_manager = tts_manager
        self.asset_manager = asset_manager
        self.current_audio_path = None
        self.tts_worker = None
        self.voices_worker = None
        self.audio_worker = None
        self.theme_worker = None
        
        # Use theme from config or default to dark
        if hasattr(tts_manager, 'config'):
            self.current_theme = tts_manager.config.get("theme", "dark")
        else:
            self.current_theme = "dark"
            
        print(f"Starting with theme: {self.current_theme}")
        
        # Set window properties
        self.setWindowTitle("ChunTTS - Advanced Text-to-Speech")
        self.setGeometry(100, 100, 1200, 700)
        self.setMinimumSize(800, 500)
        
        # Set window icon
        app_icon = self.asset_manager.load_app_icon()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)

        # Load fonts
        self.asset_manager.load_font("Inter-Regular.ttf")
        self.asset_manager.load_font("Poppins-Regular.ttf")

        # --- Central Widget and Layout ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # --- Animated Background ---
        self.background_widget = AnimatedBackground(self.central_widget)

        # --- Main Content Area ---
        self.content_widget = QWidget(self.central_widget)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_widget.setStyleSheet("background-color: transparent;")

        # --- Create UI Components ---
        self._create_header()
        self._create_body()
        self._create_footer()

        # Add content widget to main layout
        self.main_layout.addWidget(self.content_widget)
        self.background_widget.lower()  # Ensure background is behind content

        # --- Load Stylesheet ---
        self.load_theme(self.current_theme)

        # --- Connect Signals ---
        self._connect_signals()

        # --- Initial State ---
        # Start voice loading in thread
        self.start_voice_loading()

    def _create_header(self):
        self.header_frame = QFrame()
        self.header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout(self.header_frame)
        
        # Increase right margin to ensure button has enough space
        header_layout.setContentsMargins(10, 10, 15, 10)

        # Logo and title
        title_label = QLabel("ChunTTS")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title_label)

        # Theme toggle button - increased size
        self.theme_toggle = QPushButton("🌙")
        self.theme_toggle.setFixedSize(40, 40)  # Increased from 30x30 to 40x40
        self.theme_toggle.setStyleSheet("font-size: 18px; padding: 5px;")  # Better styling for the emoji
        self.theme_toggle.setToolTip("Toggle Light/Dark Theme")
        
        # Add spacer to push button to right but ensure it has space
        header_layout.addStretch(1)
        header_layout.addWidget(self.theme_toggle)

        self.content_layout.addWidget(self.header_frame)

    def _create_body(self):
        body_layout = QHBoxLayout()

        # --- Input Panel ---
        input_layout = QVBoxLayout()
        self.input_panel = QFrame()
        self.input_panel.setObjectName("inputPanel")
        input_panel_layout = QVBoxLayout(self.input_panel)

        # Text input
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Type or paste your text here...")
        self.char_count = QLabel("0 characters")
        input_panel_layout.addWidget(QLabel("Enter Text:"))
        input_panel_layout.addWidget(self.text_input)
        input_panel_layout.addWidget(self.char_count, alignment=Qt.AlignmentFlag.AlignRight)

        # Controls
        controls_frame = QFrame()
        controls_frame.setObjectName("controlsPanel")
        controls_layout = QGridLayout(controls_frame)

        # Provider selection
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(self.tts_manager.services.keys())

        # Voice selection
        self.voice_combo = QComboBox()

        # Rate and pitch controls
        self.rate_slider = QSlider(Qt.Orientation.Horizontal)
        self.pitch_slider = QSlider(Qt.Orientation.Horizontal)
        self.rate_slider.setRange(5, 20)
        self.pitch_slider.setRange(5, 20)
        self.rate_slider.setValue(10)
        self.pitch_slider.setValue(10)
        
        self.rate_label = QLabel("Rate: 1.0x")
        self.pitch_label = QLabel("Pitch: 1.0x")

        controls_layout.addWidget(QLabel("Provider:"), 0, 0)
        controls_layout.addWidget(self.provider_combo, 0, 1)
        controls_layout.addWidget(QLabel("Voice:"), 1, 0)
        controls_layout.addWidget(self.voice_combo, 1, 1)
        controls_layout.addWidget(self.rate_label, 2, 0)
        controls_layout.addWidget(self.rate_slider, 2, 1)
        controls_layout.addWidget(self.pitch_label, 3, 0)
        controls_layout.addWidget(self.pitch_slider, 3, 1)

        input_panel_layout.addWidget(controls_frame)

        # Action buttons
        button_layout = QHBoxLayout()
        self.clear_button = QPushButton("Clear")
        self.reset_button = QPushButton("Reset") # Added Reset button
        self.generate_button = QPushButton("Generate Speech")
        self.generate_button.setObjectName("generateButton")

        button_layout.addStretch(1)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.reset_button) # Added Reset button
        button_layout.addWidget(self.generate_button)
        input_panel_layout.addLayout(button_layout)

        input_layout.addWidget(self.input_panel)
        body_layout.addLayout(input_layout, stretch=7)

        # --- Output Panel ---
        output_layout = QVBoxLayout()

        # Audio player
        self.audio_player = AudioPlayerWidget()
        self.audio_player.setObjectName("audioPlayerPanel")

        # Download button
        self.download_button = QPushButton("Download Audio")
        self.download_button.setEnabled(False)

        # History list
        self.history_panel = QFrame()
        self.history_panel.setObjectName("historyPanel")
        history_layout = QVBoxLayout(self.history_panel)
        history_layout.addWidget(QLabel("Recent Generations"))
        self.history_list = HistoryListWidget()
        history_layout.addWidget(self.history_list)

        output_layout.addWidget(self.audio_player)
        output_layout.addWidget(self.download_button, alignment=Qt.AlignmentFlag.AlignCenter)
        output_layout.addWidget(self.history_panel)
        body_layout.addLayout(output_layout, stretch=5)

        self.content_layout.addLayout(body_layout)

    def _create_footer(self):
        self.footer_label = QLabel("ChunTTS © 2025 | Built with PyQt6")
        self.footer_label.setObjectName("footerLabel")
        self.content_layout.addWidget(self.footer_label, alignment=Qt.AlignmentFlag.AlignCenter)

    def _load_stylesheet(self, path):
        try:
            with open(path, "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Error loading stylesheet: {e}")

    def _connect_signals(self):
        # Text input
        self.text_input.textChanged.connect(self.update_char_count)
        
        # Provider/Voice selection
        self.provider_combo.currentTextChanged.connect(self.start_voice_loading)
        
        # Sliders
        self.rate_slider.valueChanged.connect(self.update_slider_labels)
        self.pitch_slider.valueChanged.connect(self.update_slider_labels)
        
        # Buttons
        self.clear_button.clicked.connect(self.clear_input)
        self.reset_button.clicked.connect(self.reset_application) # Connect Reset button
        self.generate_button.clicked.connect(self.start_tts_generation)
        self.download_button.clicked.connect(self.download_audio)
        self.theme_toggle.clicked.connect(self.toggle_theme)  # Connect theme toggle button
        
        # History
        self.history_list.itemClicked.connect(self.play_history_item)

    @pyqtSlot()
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        # Show a temporary indicator that theme is changing
        self.theme_toggle.setEnabled(False)
        
        # Switch theme
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.load_theme(new_theme)
        
    def load_theme(self, theme_name):
        """Load theme using worker thread"""
        # Cancel any existing theme loading thread
        if self.theme_worker and self.theme_worker.isRunning():
            self.theme_worker.quit()
            self.theme_worker.wait()
            
        # Create and start new worker
        self.theme_worker = ThemeSwitcherWorker(theme_name)
        self.theme_worker.finished.connect(self.on_theme_loaded)
        self.theme_worker.error.connect(self.on_theme_error)
        self.theme_worker.start()
    
    @pyqtSlot(str)
    def on_theme_loaded(self, stylesheet):
        """Apply loaded theme stylesheet"""
        try:
            # Toggle theme before applying stylesheet
            next_theme = "light" if self.current_theme == "dark" else "dark"
            
            # Apply the stylesheet
            self.setStyleSheet(stylesheet)
            print(f"Applied theme stylesheet: {next_theme}")
            
            # Update current theme tracking
            self.current_theme = next_theme
            
            # Update theme toggle button icon
            self.theme_toggle.setText("☀️" if self.current_theme == "light" else "🌙")
            self.theme_toggle.setEnabled(True)
            
            # Save theme preference in config
            if hasattr(self.tts_manager, 'config'):
                self.tts_manager.config.set("theme", self.current_theme)
                print(f"Saved theme preference to config: {self.current_theme}")
        except Exception as e:
            print(f"Error applying theme: {e}")
            self.theme_toggle.setEnabled(True)
    
    @pyqtSlot(str)
    def on_theme_error(self, error_message):
        """Handle theme loading error"""
        print(f"Theme error: {error_message}")
        self.theme_toggle.setEnabled(True)

    @pyqtSlot()
    def update_char_count(self):
        count = len(self.text_input.toPlainText())
        self.char_count.setText(f"{count} characters")

    @pyqtSlot(str)
    def start_voice_loading(self, provider=None):
        """Start loading voices in a separate thread"""
        if provider is None:
            provider = self.provider_combo.currentText()

        # Update UI to show loading state
        self.voice_combo.clear()
        self.voice_combo.addItem("Loading voices...")
        self.voice_combo.setEnabled(False)

        # Cancel any existing voice loading thread
        if self.voices_worker and self.voices_worker.isRunning():
            self.voices_worker.quit()
            self.voices_worker.wait()

        # Create and start new worker
        self.voices_worker = VoicesWorker(self.tts_manager, provider)
        self.voices_worker.finished.connect(self.on_voices_loaded)
        self.voices_worker.error.connect(self.on_voices_error)
        self.voices_worker.start()

    @pyqtSlot(dict)
    def on_voices_loaded(self, voices_data):
        """Handle loaded voices from worker thread"""
        provider = self.provider_combo.currentText()

        self.voice_combo.clear()
        try:
            if provider in voices_data and voices_data[provider]:
                for voice in voices_data[provider]:
                    self.voice_combo.addItem(voice['name'], voice['id'])
                self.voice_combo.setEnabled(True)
            else:
                self.voice_combo.addItem("No voices available")
                self.voice_combo.setEnabled(False)
        except Exception as e:
            print(f"Error updating voices UI: {e}")
            self.voice_combo.addItem("Error loading voices")
            self.voice_combo.setEnabled(False)

    @pyqtSlot(str)
    def on_voices_error(self, error_message):
        """Handle error in voice loading"""
        print(f"Voice loading error: {error_message}")
        self.voice_combo.clear()
        self.voice_combo.addItem("Error loading voices")
        self.voice_combo.setEnabled(False)

    @pyqtSlot(int)
    def update_slider_labels(self):
        rate = self.rate_slider.value() / 10.0
        pitch = self.pitch_slider.value() / 10.0
        self.rate_label.setText(f"Rate: {rate:.1f}x")
        self.pitch_label.setText(f"Pitch: {pitch:.1f}x")

    @pyqtSlot()
    def clear_input(self):
        self.text_input.clear()
        self.update_char_count()

    @pyqtSlot()
    def reset_application(self):
        """Resets the application state."""
        print("Resetting application state...")
        # Stop audio playback
        self.audio_player.stop()

        # Clear text input
        self.clear_input()

        # Reset sliders
        self.rate_slider.setValue(10)
        self.pitch_slider.setValue(10)
        self.update_slider_labels() # Update labels after resetting sliders

        # Clear current audio path and disable download
        self.current_audio_path = None
        self.download_button.setEnabled(False)
        self.download_button.setText("Download Audio") # Reset download button text

        # Cancel any running TTS worker - REMOVED FROM HERE
        # Let start_tts_generation handle cancelling the previous worker if needed.
        # if self.tts_worker and self.tts_worker.isRunning():
        #     print("Cancelling existing TTS worker...")
        #     self.tts_worker.cancel() # Request cancellation
        #     self.tts_worker.quit()
        #     if not self.tts_worker.wait(1000): # Wait up to 1 second
        #          print("Warning: TTS worker did not terminate gracefully.")
        #     self.tts_worker = None

        # Reset generate button state (ensure it's enabled after reset)
        self.generate_button.setEnabled(True)
        self.generate_button.setText("Generate Speech")

        # Optionally clear history (uncomment if desired)
        # self.history_list.clear_history()

        print("Application reset complete.")


    @pyqtSlot()
    def start_tts_generation(self):
        # --- Auto-Reset before generating ---
        # Stop current playback FIRST
        print("Stopping audio playback before new generation...")
        self.audio_player.stop()

        # Cancel any running TTS generation before starting new one
        if self.tts_worker and self.tts_worker.isRunning():
            print("Cancelling existing TTS worker...")
            self.tts_worker.cancel() # Request cancellation
            self.tts_worker.quit()
            if not self.tts_worker.wait(1000): # Wait up to 1 second
                 print("Warning: TTS worker did not terminate gracefully.")
            # Ensure worker reference is cleared ONLY after it's confirmed stopped/waited
            self.tts_worker = None
        # --- End Auto-Reset ---

        # NOW get the text AFTER ensuring the previous state is cleared
        text = self.text_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Empty Text", "Please enter some text to generate speech.")
            # Ensure button is re-enabled if we return early
            self.generate_button.setEnabled(True)
            self.generate_button.setText("Generate Speech")
            return

        # Disable button and show "generating" state
        self.generate_button.setEnabled(False)
        self.generate_button.setText("Generating...")

        provider = self.provider_combo.currentText()
        voice = self.voice_combo.currentData()
        rate = self.rate_slider.value() / 10.0
        pitch = self.pitch_slider.value() / 10.0

        # Create and start worker thread
        print(f"Starting new TTS worker: Provider={provider}, Voice={voice}")
        self.tts_worker = TTSWorker(
            self.tts_manager, text, provider, voice, rate, pitch
        )
        self.tts_worker.finished.connect(self.on_tts_finished)
        self.tts_worker.error.connect(self.on_tts_error)
        self.tts_worker.start()

    @pyqtSlot(str)
    def on_tts_finished(self, audio_path):
        # Ensure the worker that finished is the current one
        if self.sender() != self.tts_worker:
             print("Ignoring signal from outdated TTS worker.")
             return

        print(f"TTS finished successfully: {audio_path}")
        self.current_audio_path = audio_path
        self.audio_player.stop() # Stop any previous playback just in case
        self.audio_player.set_media(audio_path)
        self.audio_player.toggle_playback() # Start new playback
        self.download_button.setEnabled(True)

        # Add to history
        text_preview = self.text_input.toPlainText()[:40] + "..."
        provider = self.provider_combo.currentText()
        # Pass asset manager to history list if needed for icons
        if not hasattr(self.history_list, 'asset_manager') or self.history_list.asset_manager is None:
             self.history_list.asset_manager = self.asset_manager
        self.history_list.add_item(text_preview, audio_path, provider)

        self.generate_button.setEnabled(True)
        self.generate_button.setText("Generate Speech")
        self.tts_worker = None # Clear worker reference

    @pyqtSlot(str)
    def on_tts_error(self, error_message):
        # Ensure the worker that errored is the current one
        if self.sender() != self.tts_worker:
             print("Ignoring error signal from outdated TTS worker.")
             return

        print(f"TTS Error: {error_message}")
        QMessageBox.critical(self, "TTS Error", f"Error generating speech: {error_message}")
        self.generate_button.setEnabled(True)
        self.generate_button.setText("Generate Speech")
        self.download_button.setEnabled(False)
        self.tts_worker = None # Clear worker reference

    @pyqtSlot()
    def download_audio(self):
        if not self.current_audio_path or not os.path.exists(self.current_audio_path):
            QMessageBox.warning(self, "No Audio", "No audio file available to download.")
            return

        # Suggest a filename based on the audio file's stem
        from pathlib import Path
        default_filename = f"ChunTTS_{Path(self.current_audio_path).stem}.mp3"

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Audio File",
            default_filename,
            "Audio Files (*.mp3 *.wav *.ogg);;All Files (*)"
        )

        if save_path:
            # Disable button during save operation
            self.download_button.setEnabled(False)
            self.download_button.setText("Saving...")
            
            # Create and start worker thread for file copy
            self.audio_worker = AudioProcessorWorker(
                "save",
                source=self.current_audio_path,
                destination=save_path
            )
            self.audio_worker.finished.connect(self.on_download_finished)
            self.audio_worker.error.connect(self.on_download_error)
            self.audio_worker.start()

    @pyqtSlot(str)
    def on_download_finished(self, save_path):
        """Handle successful file save"""
        self.download_button.setEnabled(True)
        self.download_button.setText("Download")
        QMessageBox.information(self, "Download Complete", f"Audio saved to: {save_path}")

    @pyqtSlot(str)
    def on_download_error(self, error_message):
        """Handle error in file save"""
        self.download_button.setEnabled(True)
        self.download_button.setText("Download")
        QMessageBox.critical(self, "Download Error", f"Error saving file: {error_message}")

    @pyqtSlot(QListWidgetItem)
    def play_history_item(self, item):
        """Plays the audio associated with the clicked history item."""
        audio_path = item.data(Qt.ItemDataRole.UserRole)
        if audio_path and os.path.exists(audio_path):
            print(f"Playing from history: {audio_path}")
            self.current_audio_path = audio_path
            self.audio_player.stop() # Stop any previous playback
            self.audio_player.set_media(audio_path)
            self.audio_player.toggle_playback() # Start playback
            self.download_button.setEnabled(True)
        else:
            print(f"Warning: Audio file not found for history item: {audio_path}")
            QMessageBox.warning(self, "File Not Found", "The audio file could not be found.")
            # Consider removing the item from history if file is missing
            # row = self.history_list.row(item)
            # self.history_list.takeItem(row)


    def closeEvent(self, event):
        """Clean up threads before closing the application"""
        print("Closing application, stopping threads...")
        # Cancel all running threads
        for worker in [self.tts_worker, self.voices_worker, self.audio_worker, self.theme_worker]:
            if worker and worker.isRunning():
                print(f"Stopping worker: {type(worker).__name__}")
                if hasattr(worker, 'cancel'): # Check if worker has cancel method
                    worker.cancel()
                worker.quit()
                if not worker.wait(1000): # Wait with timeout
                    print(f"Warning: Worker {type(worker).__name__} did not terminate gracefully.")

        self.audio_player.stop()
        print("Cleanup complete. Exiting.")
        event.accept()
