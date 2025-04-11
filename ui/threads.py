from PyQt6.QtCore import QThread, pyqtSignal
import time
import os
import sys
from pathlib import Path

class TTSWorker(QThread):
    # Signals to communicate back to the main UI thread
    finished = pyqtSignal(str)  # Emits the path to the generated audio file
    error = pyqtSignal(str)     # Emits error message string
    progress = pyqtSignal(int)  # Optional: for progress updates

    def __init__(self, tts_manager, text, provider, voice, rate, pitch):
        super().__init__()
        self.tts_manager = tts_manager
        self.text = text
        self.provider = provider
        self.voice = voice
        self.rate = rate
        self.pitch = pitch
        self.process_id = None
        self.cancelled = False

    def run(self):
        """Execute the TTS generation using multiprocessing"""
        try:
            # For CPU-intensive providers like pyttsx3, use multiprocessing
            if self.provider == 'pyttsx3':
                # Start the process
                self.process_id = self.tts_manager.generate_audio_mp(
                    self.text, self.provider, self.voice, self.rate, self.pitch
                )
                
                # Poll for completion
                while not self.cancelled:
                    result = self.tts_manager.check_generation_status(self.process_id)
                    
                    if result['status'] == 'complete':
                        self.finished.emit(result['path'])
                        break
                    elif result['status'] == 'error':
                        self.error.emit(result['message'])
                        break
                    
                    # Wait before checking again
                    self.msleep(100)
            else:
                # For other providers, use the synchronous method
                output_path = self.tts_manager.generate_audio(
                    self.text, self.provider, self.voice, self.rate, self.pitch
                )
                self.finished.emit(output_path)
                
        except Exception as e:
            self.error.emit(f"Error generating audio: {str(e)}")
    
    def cancel(self):
        """Cancel the operation if running"""
        self.cancelled = True


class VoicesWorker(QThread):
    """Worker thread for loading voices asynchronously"""
    finished = pyqtSignal(dict)  # Emits dictionary of voices
    error = pyqtSignal(str)      # Emits error message string

    def __init__(self, tts_manager, provider=None):
        super().__init__()
        self.tts_manager = tts_manager
        self.provider = provider

    def run(self):
        """Fetch voices using multiprocessing for slower providers"""
        try:
            # Edge TTS is network-bound and can benefit from multiprocessing
            if self.provider == 'edge_tts':
                voices = self.tts_manager.get_available_voices_mp(self.provider)
            else:
                voices = self.tts_manager.get_available_voices(self.provider)
            self.finished.emit(voices)
        except Exception as e:
            self.error.emit(f"Error loading voices: {str(e)}")


class AudioProcessorWorker(QThread):
    """Worker thread for audio file operations"""
    finished = pyqtSignal(str)  # Emits path to processed file
    error = pyqtSignal(str)     # Emits error message string

    def __init__(self, operation, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs

    def run(self):
        """Process audio file in a separate thread"""
        try:
            result = None
            
            if self.operation == "save":
                import shutil
                source = self.kwargs.get("source")
                destination = self.kwargs.get("destination")
                shutil.copyfile(source, destination)
                result = destination
            
            # Add more operations as needed
            
            if result:
                self.finished.emit(result)
            else:
                self.error.emit("Operation not supported or failed")
        except Exception as e:
            self.error.emit(f"Error processing audio: {str(e)}")


class ThemeSwitcherWorker(QThread):
    """Worker thread for loading and applying themes"""
    finished = pyqtSignal(str)  # Emits stylesheet content
    error = pyqtSignal(str)     # Emits error message

    def __init__(self, theme_name):
        super().__init__()
        self.theme_name = theme_name
        
    def run(self):
        """Load theme stylesheet in a separate thread"""
        try:
            # Determine base path (works in both development and packaged modes)
            if getattr(sys, 'frozen', False):
                # Running as a PyInstaller bundle
                base_path = Path(sys._MEIPASS)
            else:
                # Running in normal Python environment
                base_path = Path(__file__).parent.parent
            
            # Use resolved paths
            main_style_path = base_path / "styles" / "main_style.qss"
            print(f"Looking for main style at: {main_style_path}")
            
            with open(main_style_path, "r") as f:
                stylesheet = f.read()
                
            # Load theme-specific style
            theme_path = base_path / "styles" / f"theme_{self.theme_name}.qss"
            print(f"Looking for theme at: {theme_path}")
            
            if os.path.exists(theme_path):
                with open(theme_path, "r") as f:
                    theme_style = f.read()
                    # For light theme, we need to override the dark theme styles
                    if self.theme_name == "light":
                        # Apply complete theme (not just appending)
                        stylesheet = theme_style
                    else:
                        # For dark, we can use base style as it's already dark
                        pass
            else:
                print(f"Theme file not found: {theme_path}")
            
            self.finished.emit(stylesheet)
        except Exception as e:
            print(f"Error in ThemeSwitcherWorker: {e}")
            self.error.emit(f"Error loading theme: {str(e)}")
