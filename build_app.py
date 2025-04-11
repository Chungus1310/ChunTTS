import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_app():
    """Build the application using PyInstaller with explicit exclusions"""
    print("Building ChunTTS application...")
    # Run PyInstaller with the spec file
    result = subprocess.run(['pyinstaller', 'ChunTTS.spec'], check=False)
    
    if result.returncode != 0:
        print("Error: PyInstaller build failed!")
        return False
    
    print("PyInstaller build completed successfully!")
    return True

def copy_ffmpeg_files():
    """Copy required FFmpeg executables to the distribution directory"""
    # FFmpeg configuration
    FFMPEG_BIN_DIR = Path("C:/ffmpeg-2024-03-07-git-97beb63a66-essentials_build/bin")
    DIST_DIR = Path("dist/ChunTTS")
    REQUIRED_EXECUTABLES = ["ffmpeg.exe", "ffprobe.exe"]
    
    print(f"Copying FFmpeg files from {FFMPEG_BIN_DIR} to {DIST_DIR}...")
    
    # Check if source FFmpeg directory exists
    if not FFMPEG_BIN_DIR.is_dir():
        print(f"Error: FFmpeg bin directory not found at {FFMPEG_BIN_DIR}")
        return False

    # Check if destination directory exists
    if not DIST_DIR.is_dir():
        print(f"Error: Distribution directory not found at {DIST_DIR}")
        return False

    copied_count = 0
    for exe_name in REQUIRED_EXECUTABLES:
        source_path = FFMPEG_BIN_DIR / exe_name
        destination_path = DIST_DIR / exe_name

        if source_path.is_file():
            try:
                print(f"Copying {exe_name} to {DIST_DIR}...")
                shutil.copy2(source_path, destination_path)
                copied_count += 1
                print(f"Successfully copied {exe_name}.")
            except Exception as e:
                print(f"Error copying {exe_name}: {e}")
        else:
            print(f"Warning: Required file {exe_name} not found in {FFMPEG_BIN_DIR}")

    if copied_count == len(REQUIRED_EXECUTABLES):
        print("\nFFmpeg files copied successfully.")
        return True
    elif copied_count > 0:
        print(f"\nWarning: Only {copied_count} out of {len(REQUIRED_EXECUTABLES)} required FFmpeg files were copied.")
        return True
    else:
        print("\nError: No FFmpeg files were copied.")
        return False

def cleanup_unnecessary_files():
    """Remove unnecessary files from the build to make it smaller"""
    DIST_DIR = Path("dist/ChunTTS")
    
    # List of patterns for files/directories we want to remove
    patterns_to_remove = [
        # Common unnecessary packages and files
        "*.dist-info",
        "*.egg-info",
        "__pycache__",
        "tests",
        "testing",
        "test",
        # Documentation
        "doc",
        "docs",
        "*.md", # Keep if needed, otherwise remove
        # "*.rst", # Keep if needed, otherwise remove
        # "*.txt", # Commented out or removed to prevent removing required package files
        # Examples
        "examples",
        # Development files
        ".git",
        ".github"
    ]
    
    print("Cleaning up unnecessary files to reduce package size...")
    
    for pattern in patterns_to_remove:
        if "*" in pattern:
            # It's a file pattern
            for item in DIST_DIR.glob(f"**/{pattern}"):
                if item.is_dir():
                    try:
                        shutil.rmtree(item)
                        print(f"Removed directory: {item}")
                    except Exception as e:
                        print(f"Could not remove {item}: {e}")
                else:
                    try:
                        item.unlink()
                        print(f"Removed file: {item}")
                    except Exception as e:
                        print(f"Could not remove {item}: {e}")
        else:
            # It's a specific directory name
            for item in DIST_DIR.glob(f"**/{pattern}"):
                if item.is_dir():
                    try:
                        shutil.rmtree(item)
                        print(f"Removed directory: {item}")
                    except Exception as e:
                        print(f"Could not remove {item}: {e}")
    
    print("Cleanup completed.")
    return True

if __name__ == "__main__":
    # Build the application
    if build_app():
        # Copy FFmpeg files
        copy_ffmpeg_files()
        # Cleanup unnecessary files
        cleanup_unnecessary_files()
        print("\nBuild process completed successfully!")
    else:
        print("\nBuild process failed!")
        sys.exit(1)