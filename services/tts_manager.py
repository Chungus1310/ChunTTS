import os
import multiprocessing as mp
from pathlib import Path
import uuid
from .gtts_service import GTTSService
from .edge_tts_service import EdgeTTSService
from .pyttsx3_service import Pyttsx3Service
from utils.process_manager import ProcessManager

class TTSManager:
    def __init__(self, config):
        self.config = config
        # Define output directory relative to the project root
        project_root = Path(__file__).parent.parent # Assumes tts_manager.py is in services/
        self.output_dir = project_root / "audios"
        self.output_dir.mkdir(parents=True, exist_ok=True) # Create if it doesn't exist

        # Create service instances for direct access when needed
        self.services = {
            'gtts': GTTSService(),
            'edge_tts': EdgeTTSService(),
            'pyttsx3': Pyttsx3Service()
        }
        print(f"Audio output directory: {self.output_dir}")

        # Create a multiprocessing manager
        self.mp_manager = mp.Manager()

        # Track running processes
        self.active_processes = {}
        
    def generate_audio_mp(self, text, provider='gtts', voice='', rate=1.0, pitch=1.0):
        """Generate audio using multiprocessing for CPU-intensive providers"""
        # Use multiprocessing for CPU-intensive providers (pyttsx3)
        # or network-bound providers that can benefit from being in a separate process
        
        if provider not in self.services:
            raise ValueError(f"Unsupported provider: {provider}")
        
        # Generate unique filename
        filename = f"{provider}_{uuid.uuid4().hex}.mp3"
        output_path = str(self.output_dir / filename)
        print(f"Attempting to save audio to: {output_path}")
        
        # Create result queue for the process to communicate back
        result_queue = self.mp_manager.Queue()
        
        # Start the process
        process = mp.Process(
            target=ProcessManager.run_tts_generation,
            args=(provider, text, output_path, voice, rate, pitch, result_queue)
        )
        process.start()
        
        # Store the process and queue for later retrieval
        process_id = str(uuid.uuid4())
        self.active_processes[process_id] = {
            'process': process,
            'queue': result_queue,
            'output_path': output_path
        }
        
        return process_id
    
    def check_generation_status(self, process_id):
        """Check if the generation process has completed"""
        if process_id not in self.active_processes:
            return {'status': 'error', 'message': 'Invalid process ID'}
        
        process_info = self.active_processes[process_id]
        process = process_info['process']
        queue = process_info['queue']
        
        # Check if process is done
        if not process.is_alive():
            # Process finished, check result
            if queue.empty():
                # Something went wrong, no result in queue
                return {'status': 'error', 'message': 'Process completed but no result returned'}
            
            result = queue.get()
            
            # Clean up
            del self.active_processes[process_id]
            
            # Return result
            if 'error' in result:
                return {'status': 'error', 'message': result['error']}
            else:
                return {'status': 'complete', 'path': result['path']}
        else:
            # Process still running
            return {'status': 'running'}

    # Keep the synchronous method for compatibility
    def generate_audio(self, text, provider='gtts', voice='', rate=1.0, pitch=1.0):
        """Generate audio from text using specified provider (synchronous)"""
        if provider not in self.services:
            raise ValueError(f"Unsupported provider: {provider}")

        service = self.services[provider]

        # Generate unique filename
        filename = f"{provider}_{uuid.uuid4().hex}.mp3"
        output_path = self.output_dir / filename
        print(f"Attempting to save audio to: {output_path}")

        try:
            # Generate audio
            service.synthesize(text, str(output_path), voice, rate, pitch)
            if not output_path.exists():
                raise FileNotFoundError(f"TTS service failed to create file at {output_path}")
            print(f"Audio successfully generated at: {output_path}")
            return str(output_path)
        except Exception as e:
            print(f"Error during synthesis or file check: {e}")
            raise
    
    def get_available_voices_mp(self, provider):
        """Get available voices using multiprocessing"""
        if provider not in self.services:
            return {provider: []}
        
        # Create result queue for the process to communicate back
        result_queue = self.mp_manager.Queue()
        
        # Start the process
        process = mp.Process(
            target=ProcessManager.run_voice_loading,
            args=(provider, result_queue)
        )
        process.start()
        
        # Wait for completion (could be made non-blocking in the future)
        process.join()
        
        # Get result
        if not result_queue.empty():
            result = result_queue.get()
            if 'error' in result:
                print(f"Error getting voices for {provider}: {result['error']}")
                return {provider: []}
            else:
                return {provider: result['voices']}
        else:
            return {provider: []}

    # Keep the original method for compatibility
    def get_available_voices(self, provider=None):
        """Get available voices for specified provider or all providers (synchronous)"""
        result = {}
        target_services = self.services.items()
        if provider and provider in self.services:
            target_services = [(provider, self.services[provider])]
        elif provider:
            return {provider: []}

        for name, service in target_services:
            try:
                result[name] = service.get_voices()
            except Exception as e:
                print(f"Error getting voices for {name}: {e}")
                result[name] = []
        return result

    def cleanup_old_audio(self, max_age_days=7):
        """Clean up old audio files"""
        try:
            current_time = Path().stat().st_mtime
            for file in self.output_dir.glob("*.mp3"):
                file_age_days = (current_time - file.stat().st_mtime) / (24 * 3600)
                if file_age_days > max_age_days:
                    file.unlink()
        except Exception as e:
            print(f"Error during cleanup: {e}")
