from flask import Flask, request, jsonify, Response
import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import Voice, VoiceSettings

load_dotenv()

app = Flask(__name__)

try:
    elevenlabs_client = ElevenLabs(api_key=os.environ.get("ELEVENLABS_API_KEY"))
    print("ElevenLabs Client Initialized.")
except Exception as e:
    print(f"Error initializing ElevenLabs client: {e}")
    elevenlabs_client = None

# --- THIS IS THE KEY CHANGE ---
# This endpoint now streams audio directly back to the client.
@app.route('/api/generate-audio-stream', methods=['POST'])
def generate_audio_stream_handler():
    if not elevenlabs_client:
        return jsonify({"error": "ElevenLabs client not initialized."}), 503

    data = request.get_json()
    text_to_speak = data.get('text')
    if not text_to_speak:
        return jsonify({"error": "Parameter 'text' is missing"}), 400

    def audio_stream_generator():
        """A generator function that streams audio from ElevenLabs."""
        print(f"Streaming audio for text: '{text_to_speak}'")
        try:
            # Call ElevenLabs API with stream=True
            audio_stream = elevenlabs_client.generate(
                text=text_to_speak,
                voice=Voice(
                    voice_id='56AoDkrOh6qfVPDXZ7Pt',
                    settings=VoiceSettings(stability=0.71, similarity_boost=0.5, style=0.0, use_speaker_boost=True)
                ),
                model="eleven_multilingual_v2",
                stream=True  # This is the magic parameter!
            )
            
            # Yield each chunk of audio data as it arrives
            for chunk in audio_stream:
                if chunk:
                    yield chunk
            print("Finished streaming from ElevenLabs.")
        except Exception as e:
            print(f"Error during ElevenLabs stream: {e}")

    # Return a Flask Response object with the generator and correct mimetype
    return Response(audio_stream_generator(), mimetype='audio/mpeg')

@app.route('/')
def home():
    return "Streaming Audio Generation Backend is running!"
