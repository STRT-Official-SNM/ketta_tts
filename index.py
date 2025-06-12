# File: audio_backend.py

from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
import base64

from elevenlabs.client import ElevenLabs
from elevenlabs import Voice, VoiceSettings

# Load environment variables from .env file for local testing
load_dotenv()

# --- INITIALIZE FLASK APP ---
app = Flask(__name__)

# --- LOAD API KEYS AND INITIALIZE CLIENTS ---
try:
    # Initialize the ElevenLabs Client
    elevenlabs_client = ElevenLabs(
      api_key=os.environ.get("ELEVENLABS_API_KEY")
    )
    print("ElevenLabs Client Initialized.")
except Exception as e:
    print(f"Error initializing ElevenLabs client: {e}")
    elevenlabs_client = None

# --- API ENDPOINT FOR AUDIO GENERATION ---
# Vercel will route requests to this function based on vercel.json
@app.route('/api/generate-audio', methods=['POST'])
def generate_audio_handler():
    if not elevenlabs_client:
        return jsonify({"error": "ElevenLabs client not initialized. Check API Key."}), 503

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    text_to_speak = data.get('text')
    if not text_to_speak:
        return jsonify({"error": "Parameter 'text' is missing"}), 400

    try:
        print(f"Generating audio for text: '{text_to_speak}'")
        audio_stream = elevenlabs_client.generate(
            text=text_to_speak,
            voice=Voice(
                voice_id='56AoDkrOh6qfVPDXZ7Pt', # Your chosen voice ID
                settings=VoiceSettings(stability=0.71, similarity_boost=0.5, style=0.0, use_speaker_boost=True)
            ),
            model="eleven_multilingual_v2"
        )
        audio_bytes = b"".join(audio_stream)
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        print("Audio generated and encoded successfully.")
        return jsonify({"audio_content": audio_base64})

    except Exception as e:
        print(f"An error occurred during audio generation: {e}")
        return jsonify({"error": "An internal error occurred"}), 500

# Health check endpoint for the root URL
@app.route('/', methods=['GET'])
def home():
    return "Audio Generation Backend is running!"

# This block is for local testing only. Vercel will not use it.
if __name__ == '__main__':
    app.run(debug=True, port=5001)
