from gtts import gTTS

class GTTSService:
    def __init__(self):
        self.langs = {
            'en-US': 'English (US)',
            'en-GB': 'English (UK)',
            'fr-FR': 'French',
            'de-DE': 'German',
            'es-ES': 'Spanish',
            'it-IT': 'Italian',
            'ja-JP': 'Japanese',
            'ko-KR': 'Korean',
            'zh-CN': 'Chinese (Mainland)',
            'zh-TW': 'Chinese (Taiwan)',
        }

    def synthesize(self, text, output_path, voice='en-US', rate=1.0, pitch=1.0):
        """
        Synthesize speech using Google Text-to-Speech
        Note: gTTS doesn't support rate/pitch modification directly
        """
        lang = voice.split('-')[0] if voice else 'en'
        tts = gTTS(text=text, lang=lang, slow=rate < 1.0)
        tts.save(output_path)
        return output_path

    def get_voices(self):
        """Get available voices/languages"""
        return [{'id': lang_code, 'name': name} for lang_code, name in self.langs.items()]
