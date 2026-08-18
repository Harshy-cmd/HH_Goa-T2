import os
import sys

from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()

API_KEY = os.getenv("SARVAM_API_KEY")

if not API_KEY:
    print("ERROR: SARVAM_API_KEY is missing from backend/.env")
    sys.exit(1)

AUDIO_FILE = r"C:\PATH\TO\YOUR\test_voice.wav"

if not os.path.exists(AUDIO_FILE):
    print(f"ERROR: Audio file not found: {AUDIO_FILE}")
    sys.exit(1)

print("Initializing Sarvam Saaras v3...")

client = SarvamAI(
    api_subscription_key=API_KEY
)

try:
    with open(AUDIO_FILE, "rb") as audio:
        response = client.speech_to_text.transcribe(
            file=audio,
            model="saaras:v3",
            language_code="unknown",
            mode="transcribe",
        )

    print("\n==============================")
    print("SARVAM STT TEST SUCCESS")
    print("==============================")

    print("Transcript:")
    print(response.transcript)

    print("\nDetected language:")
    print(response.language_code)

    print("\nLanguage probability:")
    print(response.language_probability)

    print("\nRequest ID:")
    print(response.request_id)

except Exception as e:
    print("\n==============================")
    print("SARVAM STT TEST FAILED")
    print("==============================")
    print(type(e).__name__)
    print(str(e))