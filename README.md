```markdown
# AI Voice Agent

A real‑time, context‑aware voice assistant built with Flask, Socket.IO, LiveKit, OpenAI, and ElevenLabs.

---

## Table of Contents

- [Features](#features)  
- [Architecture](#architecture)  
- [Prerequisites](#prerequisites)  
- [Installation](#installation)  
- [Configuration](#configuration)  
- [Running the App](#running-the-app)  
- [Usage](#usage)  
- [Tech Stack](#tech-stack)  
- [Contributing](#contributing)  
- [License](#license)  
- [Contact](#contact)  

---

## Features

- **WebRTC audio streaming** via LiveKit  
- **Real‑time speech-to-text** using OpenAI’s STT API  
- **GPT‑powered response generation** for context‑aware dialogue  
- **High‑fidelity text-to-speech** with ElevenLabs  
- **Low‑latency, bidirectional** voice communication  
- Conversation logging for analytics  

---

## Architecture

```

\[Browser] ←── WebRTC/DataChannel ──→ \[Flask + Socket.IO + LiveKit] ←───→ \[OpenAI STT / GPT]
↓
\[ElevenLabs TTS → Browser audio]

````

1. **Frontend (index.html)**  
   - Captures microphone audio via LiveKit SDK  
   - Streams audio & metadata over WebRTC/data channels  
2. **Backend (app.py)**  
   - Manages signaling and audio relay with Socket.IO + LiveKit  
   - Forwards audio chunks to OpenAI STT → gets transcript  
   - Sends transcript to GPT → receives text response  
   - Sends text to ElevenLabs TTS → streams speech back  
   - Logs conversation metadata via REST endpoint  

---

## Prerequisites

- Python 3.9+  
- pip  
- LiveKit server (self‑hosted or LiveKit Cloud)  
- OpenAI API key  
- ElevenLabs API key  

---

## Installation

1. **Clone the repo**  
   ```bash
   git clone https://github.com/AaqibAnsari/AI-Voice-Agent.git
   cd AI-Voice-Agent/backend
````

2. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Serve the frontend**

   * Either open `frontend/index.html` directly in your browser
   * Or run a simple HTTP server in the `frontend` folder:

     ```bash
     cd ../frontend
     python -m http.server 8000
     ```

---

## Configuration

Copy `.env.example` to `.env` (create if missing) and set:

```ini
LIVEKIT_URL=https://your-livekit-host
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret

OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

---

## Running the App

From the `backend` folder:

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

* Backend: `http://localhost:5000`
* Frontend (if using simple server): `http://localhost:8000`

---

## Usage

1. Open the frontend URL in your browser.
2. Grant microphone access.
3. Speak; your words will be transcribed, processed by GPT, and returned as speech.
4. View logs and transcripts in the backend console or via the REST analytics endpoint.

---

## Tech Stack

* **Backend**: Flask, python‑socketio, LiveKit Python SDK
* **Frontend**: HTML, JavaScript, LiveKit Web SDK
* **AI Services**: OpenAI (STT & GPT), ElevenLabs TTS
* **Deployment**: any WSGI server (gunicorn/uvicorn), Dockerizable

---

## Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add my feature"`
4. Push to branch: `git push origin feature/my-feature`
5. Open a Pull Request

Please follow the existing code style and add tests for new functionality.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Contact

**Aaqib Ansari**

* GitHub: [@AaqibAnsari](https://github.com/AaqibAnsari)
