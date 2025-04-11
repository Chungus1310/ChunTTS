import os
import shutil
from pathlib import Path

def setup_asset_structure():
    """Create the asset directory structure and copy default assets"""
    base_dir = Path(__file__).parent
    
    # Create directories
    dirs = [
        base_dir / "fonts",
        base_dir / "icons",
        base_dir / "logo"
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(exist_ok=True)
        print(f"Created directory: {dir_path}")
        
    # Create a placeholder logo
    create_placeholder_logo(base_dir / "logo" / "app_logo.png")
    create_placeholder_logo(base_dir / "logo" / "favicon.ico")
    
    # Create placeholder icons
    icons = ["dark.png", "light.png", "gtts.png", "edge_tts.png", "pyttsx3.png"]
    for icon in icons:
        create_placeholder_icon(base_dir / "icons" / icon)
    
    print("Asset structure setup complete!")

def create_placeholder_logo(path):
    """Create a simple placeholder logo file"""
    # In a real application, you'd include actual logo files
    with open(path, 'wb') as f:
        f.write(b'PLACEHOLDER LOGO - Replace with real logo file')
    print(f"Created placeholder logo: {path}")

def create_placeholder_icon(path):
    """Create a simple placeholder icon file"""
    # In a real application, you'd include actual icon files
    with open(path, 'wb') as f:
        f.write(b'PLACEHOLDER ICON - Replace with real icon file')
    print(f"Created placeholder icon: {path}")

if __name__ == "__main__":
    setup_asset_structure()