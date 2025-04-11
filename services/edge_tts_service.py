import asyncio
import edge_tts

class EdgeTTSService:
    def __init__(self):
        self._voices = None

    def synthesize(self, text, output_path, voice='en-US-JennyNeural', rate=1.0, pitch=1.0):
        """Synthesize speech using Microsoft Edge TTS"""
        # Convert rate (e.g., 1.0, 1.5) to percentage format (e.g., "+0%", "+50%")
        rate_percentage = (rate - 1.0) * 100
        rate_str = f"{'+' if rate_percentage >= 0 else ''}{rate_percentage:.0f}%"

        # Pitch is not directly supported by edge-tts library's Communicate,
        # but can sometimes be embedded in SSML if needed. Ignoring for now.

        async def _synthesize():
            communicate = edge_tts.Communicate(text, voice, rate=rate_str)
            await communicate.save(output_path)

        # Run async code in sync context
        try:
            asyncio.run(_synthesize())
        except Exception as e:
             # Catch potential asyncio errors if loop is already running etc.
             print(f"Error running Edge TTS async task: {e}")
             # Fallback or alternative execution might be needed in complex GUI apps
             # For now, re-raise to indicate failure
             raise
        return output_path

    def get_voices(self):
        """Get available voices from Edge TTS"""
        if self._voices is None:
            async def _get_voices():
                self._voices = []
                voices = await edge_tts.list_voices()
                for voice in voices:
                    # Adjust keys based on potential library changes
                    # Common keys are 'Name', 'ShortName', 'Gender', 'Locale'
                    display_name = voice.get('DisplayName', voice.get('Name', voice.get('ShortName'))) # Try multiple keys
                    locale_name = voice.get('LocaleName', voice.get('Locale', 'N/A')) # Try multiple keys
                    self._voices.append({
                        'id': voice['ShortName'],
                        'name': f"{locale_name} - {display_name}", # Use fetched names
                        'gender': voice['Gender'],
                        'locale': voice['Locale']
                    })
                return self._voices

            # Run async code in sync context
            self._voices = asyncio.run(_get_voices())

        return self._voices
