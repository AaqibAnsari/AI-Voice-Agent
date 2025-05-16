import os
import uuid
import numpy as np
import torch
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
from openai import OpenAI
from scipy.io.wavfile import write
from starlette.websockets import WebSocketState

# --- Load environment variables ---
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# --- FastAPI app ---
app = FastAPI()

# --- Directories ---
TEMP_AUDIO_DIR = "temp_audio"
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)

# --- Load Silero VAD model ---
vad_model, vad_utils = torch.hub.load(
    'snakers4/silero-vad', 'silero_vad', force_reload=False
)
get_speech_ts = vad_utils[0]

# --- OpenAI client ---
openai_client = OpenAI(api_key=OPENAI_KEY)

# --- Process and respond to audio ---
async def process_audio(ws: WebSocket, samples: np.ndarray):
    try:
        print("[process_audio] Running VAD...")

        # Normalize and run VAD
        if samples.dtype != np.float32:
            samples = samples.astype(np.float32) / 32768.0
        segments = get_speech_ts(samples, vad_model, sampling_rate=16000)
        if not segments:
            await ws.send_json({'type': 'log', 'text': 'No speech detected.'})
            return

        # Concatenate speech segments and save WAV
        speech = np.concatenate([samples[s['start']:s['end']] for s in segments])
        wav_path = os.path.join(TEMP_AUDIO_DIR, f"speech_{uuid.uuid4().hex}.wav")
        write(wav_path, 16000, (speech * 32767).astype(np.int16))
        print(f"[process_audio] VAD speech saved to {wav_path}")

        # Transcribe with Whisper
        with open(wav_path, "rb") as f:
            transcript_resp = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        transcript = transcript_resp.text
        print(f"[process_audio] Transcription: {transcript}")
        await ws.send_json({'type': 'transcript', 'text': transcript})

        # GPT-4 medical assistant
        gpt_response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {'role': 'system', 'content': (
                    "You are a concise, knowledgeable medical assistant. "
                    "Answer health-related queries clearly and briefly."
                )},
                {'role': 'user', 'content': transcript}
            ]
        )
        reply = gpt_response.choices[0].message.content.strip()
        print(f"[process_audio] GPT-4 reply: {reply}")
        await ws.send_json({'type': 'response_text', 'text': reply})

        # OpenAI TTS
        print("[process_audio] Generating TTS via OpenAI...")
        tts_resp = openai_client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=reply,
            response_format="mp3"
        )
        audio_bytes = tts_resp.content
        total_bytes = len(audio_bytes)
        print(f"[process_audio] Received {total_bytes} bytes of audio from OpenAI TTS")

        # Stream MP3 chunks
        chunk_size = 4096
        for i in range(0, total_bytes, chunk_size):
            chunk = audio_bytes[i:i+chunk_size]
            try:
                await ws.send_bytes(chunk)
            except WebSocketDisconnect:
                print("[process_audio] Client disconnected during TTS streaming.")
                return

        print("[process_audio] TTS stream complete.")
        await ws.send_json({'type': 'tts_end'})

    except Exception as e:
        print(f"[process_audio] Error: {e}")
        if ws.client_state not in [WebSocketState.CLOSED, WebSocketState.CLOSING]:
            await ws.send_json({'type': 'error', 'text': str(e)})

# --- WebSocket endpoint ---
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    print("[ws] Connected.")

    audio_buffer = bytearray()
    try:
        while True:
            data = await ws.receive_bytes()
            if not data:
                break
            audio_buffer.extend(data)
    except WebSocketDisconnect:
        print("[ws] Disconnected.")

    print(f"[ws] Received {len(audio_buffer)} bytes.")
    if not audio_buffer:
        if ws.client_state not in [WebSocketState.CLOSED, WebSocketState.CLOSING]:
            await ws.send_json({'type': 'log', 'text': 'No audio data received.'})
        return

    pcm_samples = np.frombuffer(audio_buffer, dtype=np.int16)
    await process_audio(ws, pcm_samples)
