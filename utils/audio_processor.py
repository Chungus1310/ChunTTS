import numpy as np
from pydub import AudioSegment
import os

class AudioProcessor:
    @staticmethod
    def get_audio_duration(file_path):
        """Get the duration of an audio file in milliseconds"""
        try:
            audio = AudioSegment.from_file(file_path)
            return len(audio)
        except Exception as e:
            print(f"Error getting audio duration: {e}")
            return 0

    @staticmethod
    def get_audio_data(file_path):
        """Get audio data as numpy array for visualization"""
        try:
            audio = AudioSegment.from_file(file_path)
            samples = np.array(audio.get_array_of_samples())
            
            # Convert to float32 and normalize
            samples = samples.astype(np.float32)
            samples = samples / np.iinfo(np.int16).max
            
            return samples
        except Exception as e:
            print(f"Error processing audio data: {e}")
            return np.array([])

    @staticmethod
    def adjust_audio(file_path, output_path, speed=1.0, pitch=1.0):
        """Adjust audio speed and pitch"""
        try:
            audio = AudioSegment.from_file(file_path)
            
            # Apply speed change if needed
            if speed != 1.0:
                speed_changed = audio._spawn(audio.raw_data, overrides={
                    "frame_rate": int(audio.frame_rate * speed)
                })
                audio = speed_changed.set_frame_rate(audio.frame_rate)
            
            # Export the modified audio
            audio.export(output_path, format="mp3")
            return output_path
        except Exception as e:
            print(f"Error adjusting audio: {e}")
            return None

    @staticmethod
    def get_waveform_data(file_path, num_points=100):
        """Get waveform data for visualization"""
        try:
            audio = AudioSegment.from_file(file_path)
            samples = np.array(audio.get_array_of_samples())
            
            # Resample to desired number of points
            samples = samples.astype(np.float32)
            samples = samples / np.iinfo(np.int16).max
            
            # Calculate points for visualization
            chunk_size = len(samples) // num_points
            if chunk_size < 1:
                return samples
            
            points = []
            for i in range(0, len(samples), chunk_size):
                chunk = samples[i:i + chunk_size]
                if len(chunk) > 0:
                    points.append(np.max(np.abs(chunk)))
            
            return np.array(points)
        except Exception as e:
            print(f"Error getting waveform data: {e}")
            return np.zeros(num_points)
