import os
import requests
from dotenv import load_dotenv

load_dotenv()

class ElevenLabsClient:
    def __init__(self):
        self.api_key = os.getenv('ELEVEN_LABS_API_KEY')
        self.base_url = "https://api.elevenlabs.io/v1"

        if not self.api_key:
            raise ValueError("ELEVEN_LABS_API_KEY bulunamadı! .env dosyanızı kontrol edin.")

    def get_all_voices(self):
        """Mevcut tüm sesleri listeler."""
        response = requests.get(
            f"{self.base_url}/voices",
            headers={"Accept": "application/json", "xi-api-key": self.api_key, "Content-Type": "application/json"}
        )
        data = response.json()

        voices = {voice["name"]: voice["voice_id"] for voice in data.get("voices", [])}

        for name, voice_id in voices.items():
            print(f"{name}; {voice_id}")

        return voices  # Sesleri dict olarak döndür

    def convert_text_to_audio(self, text: str, voice_id: str = "PdYVUd1CAGSXsTvZZTNn", output_file: str = "output.mp3"):
        """Metni sese dönüştürüp mp3 olarak kaydeder."""
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }

        data = {
            "text": text,
            "model_id": "eleven_flash_v2_5",
            "voice_settings": {
                "stability": 0.4,
                "similarity_boost": 0.5
            }
        }

        url = f"{self.base_url}/text-to-speech/{voice_id}"
        response = requests.post(url, json=data, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Hata oluştu! API yanıtı: {response.text}")

        with open(output_file, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)

        print(f"Ses kaydedildi: {output_file}")
        return output_file