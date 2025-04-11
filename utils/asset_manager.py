import os
import sys
from pathlib import Path
from PyQt6.QtGui import QIcon, QPixmap, QFontDatabase, QFont

class AssetManager:
    """Handles loading and management of application assets"""
    
    def __init__(self):
        # Determine application base path
        if getattr(sys, 'frozen', False):
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            self.base_path = Path(sys._MEIPASS)
        else:
            self.base_path = Path(__file__).parent.parent
        
        # Asset directories
        self.fonts_dir = self.base_path / "fonts"  # Changed from assets/fonts to fonts
        self.icons_dir = self.base_path / "assets" / "icons"
        self.logo_dir = self.base_path / "assets" / "logo"
        
        # Track loaded fonts
        self.loaded_fonts = {}
        
        # Initialize essential assets
        self._initialize()
    
    def _initialize(self):
        """Initialize essential assets"""
        print(f"Initializing assets from {self.base_path}")
        print(f"Fonts directory: {self.fonts_dir}")
        
        # Create directories if they don't exist
        for dir_path in [self.icons_dir, self.logo_dir]:
            if not dir_path.exists():
                print(f"Creating directory: {dir_path}")
                dir_path.mkdir(parents=True, exist_ok=True)
    
    def load_font(self, font_name):
        """Load a font from assets and return its ID"""
        if font_name in self.loaded_fonts:
            return self.loaded_fonts[font_name]
        
        # Try to find the font file
        font_path = self.fonts_dir / font_name
        if font_path.exists():
            font_id = QFontDatabase.addApplicationFont(str(font_path))
            if font_id != -1:
                self.loaded_fonts[font_name] = font_id
                print(f"Loaded font: {font_name} with ID {font_id}")
                return font_id
        
        # If direct file not found, try to find it from metadata
        metadata_path = self.fonts_dir / "font_paths.txt"
        if metadata_path.exists():
            try:
                with open(metadata_path, "r") as f:
                    for line in f:
                        if line.startswith(f"{font_name}:"):
                            relative_path = line.split(":", 1)[1].strip()
                            font_path = self.fonts_dir / relative_path
                            if font_path.exists():
                                print(f"Loading font from path: {font_path}")
                                font_id = QFontDatabase.addApplicationFont(str(font_path))
                                if font_id != -1:
                                    self.loaded_fonts[font_name] = font_id
                                    print(f"Loaded font: {font_name} with ID {font_id}")
                                    return font_id
                            else:
                                print(f"Font file not found: {font_path}")
            except Exception as e:
                print(f"Error reading font metadata: {e}")
        
        # If we get here, try to use a system font as fallback
        print(f"Font '{font_name}' not found, using system font as fallback")
        return -1  # Return -1 to indicate font wasn't loaded
    
    def load_icon(self, icon_name):
        """Load an icon from assets"""
        icon_path = self.icons_dir / icon_name
        if icon_path.exists():
            return QIcon(str(icon_path))
        else:
            print(f"Icon not found: {icon_path}")
            return QIcon()  # Return empty icon
    
    def load_app_icon(self):
        """Load the application icon"""
        # Try several possible icon formats
        icon_formats = ["favicon.ico", "app_logo.png", "app_icon.ico", "logo.png"]
        for icon_format in icon_formats:
            icon_path = self.logo_dir / icon_format
            if icon_path.exists():
                return QIcon(str(icon_path))
        
        print("App icon not found!")
        return QIcon()  # Return empty icon
    
    def get_provider_icon(self, provider_name):
        """Get icon for a specific TTS provider"""
        # Look for provider-specific icon
        icon_name = f"{provider_name}.png"
        icon = self.load_icon(icon_name)
        
        # If not found, return default icon
        if icon.isNull():
            return self.load_icon("default_provider.png")
        
        return icon