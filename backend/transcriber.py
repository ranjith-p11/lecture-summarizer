"""
transcriber.py – Audio/video transcription using OpenAI Whisper
               – YouTube audio extraction using yt-dlp
"""
import os
import tempfile
import whisper

# Load Whisper models dynamically to save memory if unused.
_models = {}

def get_model(size: str = "base"):
    if size not in _models:
        print(f"[Transcriber] Loading Whisper model: {size}...")
        _models[size] = whisper.load_model(size)
        print(f"[Transcriber] Whisper model '{size}' loaded.")
    return _models[size]


def transcribe_file(file_path: str, model_size: str = "base") -> dict:
    """
    Transcribe an audio/video file using Whisper.

    Args:
        file_path: Absolute path to the audio/video file.
        model_size: Size of the model to use ("base", "small", "medium").

    Returns:
        Dict containing transcript text, language detected, and segments.
    """
    print(f"[Transcriber] Transcribing file: {file_path} using {model_size}")
    model = get_model(model_size)
    result = model.transcribe(file_path)
    
    return {
        "text": result.get("text", "").strip(),
        "language": result.get("language", "unknown"),
        "segments": result.get("segments", [])
    }


def transcribe_youtube(url: str, model_size: str = "base") -> dict:
    import yt_dlp

    with tempfile.TemporaryDirectory() as tmpdir:
        output_template = os.path.join(tmpdir, "audio.%(ext)s")

        ydl_opts = {
    "format": "bestaudio/best",
    "outtmpl": output_template,
    "quiet": False,
    "noplaylist": True,
    "geo_bypass": True,
    "retries": 3,
    "cookiefile": os.path.join(os.path.dirname(__file__), "cookies.txt"),  # 🔥 FIX
    "http_headers": {
        "User-Agent": "Mozilla/5.0"
    },
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
}

        print(f"[Transcriber] Downloading audio from: {url}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Find downloaded file
        audio_file = None
        for fname in os.listdir(tmpdir):
            if fname.startswith("audio."):
                audio_file = os.path.join(tmpdir, fname)
                break

        if not audio_file:
            raise FileNotFoundError("Audio file not found.")

        # Pass the desired model size from the user down to transcribe_file
        return transcribe_file(audio_file, model_size)


def transcribe_text_passthrough(text: str) -> str:
    """
    When the user pastes text directly, no transcription needed.
    Just return the text as-is.
    """
    return text.strip()
