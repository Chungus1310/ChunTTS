import pyttsx3

class Pyttsx3Service:
    def __init__(self):
        self.engine = pyttsx3.init()
        self._voices = None

    def synthesize(self, text, output_path, voice=None, rate=1.0, pitch=1.0):
        """Synthesize speech using local pyttsx3"""
        try:
            # Set voice if specified
            if voice and self.engine.getProperty('voices'):
                voices = self.engine.getProperty('voices')
                for v in voices:
                    if v.id == voice:
                        self.engine.setProperty('voice', v.id)
                        break

            # Set rate (pyttsx3 uses words per minute, default is 200)
            current_rate = self.engine.getProperty('rate')
            self.engine.setProperty('rate', int(current_rate * rate))

            # Set volume (as proxy for pitch since pyttsx3 doesn't support pitch)
            self.engine.setProperty('volume', min(1.0, pitch))

            # Save to file
            self.engine.save_to_file(text, output_path)
            self.engine.runAndWait()
            return output_path

        except Exception as e:
            print(f"Error in pyttsx3 synthesis: {e}")
            raise

    def get_voices(self):
        """Get available voices from the system"""
        if self._voices is None:
            self._voices = []
            try:
                print("pyttsx3: Initializing engine...")
                engine_voices = self.engine.getProperty('voices')
                print(f"pyttsx3: Found {len(engine_voices)} voices raw.")
                for i, voice in enumerate(engine_voices):
                    try:
                        voice_info = {
                            'id': voice.id,
                            'name': voice.name,
                            'languages': voice.languages,
                            'gender': getattr(voice, 'gender', None)
                        }
                        self._voices.append(voice_info)
                        # print(f"pyttsx3: Added voice {i+1}: {voice_info}") # Uncomment for very detailed logs
                    except Exception as e_voice:
                        print(f"pyttsx3: Error processing voice {i}: {e_voice}")

            except Exception as e:
                print(f"Error getting pyttsx3 voices: {e}")
            print(f"pyttsx3: Finished processing. Total voices added: {len(self._voices)}")

        return self._voices
