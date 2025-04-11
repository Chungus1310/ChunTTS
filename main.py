import sys
import os
import multiprocessing
from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap

from ui.main_window import MainWindow
from services.tts_manager import TTSManager
from utils.config_manager import ConfigManager
from utils.asset_manager import AssetManager

def check_assets():
    """Check if assets are available, create them if not"""
    # Check for assets directory structure
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir, exist_ok=True)
        
    # Check for subdirectories
    for subdir in ["fonts", "icons", "logo"]:
        subdir_path = os.path.join(assets_dir, subdir)
        if not os.path.exists(subdir_path):
            os.makedirs(subdir_path, exist_ok=True)
    
    # If font files don't exist, create a note file
    font_dir = os.path.join(assets_dir, "fonts")
    if not any(f.endswith('.ttf') for f in os.listdir(font_dir) if os.path.isfile(os.path.join(font_dir, f))):
        note_path = os.path.join(font_dir, "README.txt")
        with open(note_path, "w") as f:
            f.write("Place font files (TTF) here.\n")
            f.write("Recommended: Inter-Regular.ttf and Poppins-Regular.ttf\n")
    
    # If icon files don't exist, create placeholders
    icon_dir = os.path.join(assets_dir, "icons")
    for icon in ["dark.png", "light.png", "gtts.png", "edge_tts.png", "pyttsx3.png"]:
        icon_path = os.path.join(icon_dir, icon)
        if not os.path.exists(icon_path):
            # Create a simple placeholder file
            with open(icon_path, "w") as f:
                f.write("Placeholder for icon")
    
    # If logo files don't exist, create placeholders
    logo_dir = os.path.join(assets_dir, "logo")
    for logo in ["app_logo.png", "favicon.ico"]:
        logo_path = os.path.join(logo_dir, logo)
        if not os.path.exists(logo_path):
            with open(logo_path, "w") as f:
                f.write("Placeholder for logo")

if __name__ == '__main__':
    # Enable multiprocessing support for Windows
    multiprocessing.freeze_support()
    
    # Create application
    app = QApplication(sys.argv)
    
    # Show a splash screen if a logo exists
    splash = None
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo", "app_logo.png")
    if os.path.exists(logo_path):
        try:
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                splash = QSplashScreen(pixmap)
                splash.show()
                app.processEvents()
        except Exception as e:
            print(f"Error showing splash screen: {e}")
    
    # Check and initialize assets
    check_assets()
    
    # Initialize asset manager
    asset_manager = AssetManager()
    
    # Load config and initialize TTS manager
    config = ConfigManager('config.json')
    tts_manager = TTSManager(config)
    
    # Create and show main window
    main_win = MainWindow(tts_manager, asset_manager)
    
    # Close splash if shown
    if splash:
        splash.finish(main_win)
    
    main_win.show()
    
    sys.exit(app.exec())
