import multiprocessing as mp
import json
import os
from pathlib import Path

class ProcessManager:
    """Manages multiprocessing operations for CPU-intensive tasks"""

    @staticmethod
    def run_tts_generation(provider_name, text, output_path, voice, rate, pitch, result_queue):
        """Run TTS generation in a separate process"""
        try:
            service = None
            # Import services here to avoid circular imports
            if provider_name == 'gtts':
                from services.gtts_service import GTTSService
                service = GTTSService()
            elif provider_name == 'edge_tts':
                from services.edge_tts_service import EdgeTTSService
                service = EdgeTTSService()
                # Rate conversion is handled within EdgeTTSService.synthesize now
            elif provider_name == 'pyttsx3':
                from services.pyttsx3_service import Pyttsx3Service
                service = Pyttsx3Service()
            else:
                result_queue.put({"error": f"Unknown provider: {provider_name}"})
                return

            # Generate audio
            # Pass the original float rate; the service handles specific formatting if needed
            service.synthesize(text, output_path, voice, rate, pitch)

            # Check if file exists
            if os.path.exists(output_path):
                result_queue.put({"path": output_path})
            else:
                result_queue.put({"error": f"Failed to generate audio at {output_path}"})
        except Exception as e:
            result_queue.put({"error": str(e)})

    @staticmethod
    def run_voice_loading(provider_name, result_queue):
        """Load voices for a provider in a separate process"""
        try:
            service = None
            # Import services here
            if provider_name == 'gtts':
                from services.gtts_service import GTTSService
                service = GTTSService()
            elif provider_name == 'edge_tts':
                from services.edge_tts_service import EdgeTTSService
                service = EdgeTTSService()
            elif provider_name == 'pyttsx3':
                from services.pyttsx3_service import Pyttsx3Service
                service = Pyttsx3Service()
            else:
                result_queue.put({"error": f"Unknown provider: {provider_name}"})
                return

            # Get voices
            voices = service.get_voices()
            result_queue.put({"voices": voices})

        except Exception as e:
            result_queue.put({"error": str(e)})