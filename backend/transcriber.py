"""
transcriber.py – Audio/video transcription using OpenAI Whisper
               – YouTube audio extraction using yt-dlp
"""
import os
import tempfile
import whisper

# Load Whisper model once at module level (change to 'small' or 'medium' for higher accuracy)
MODEL_SIZE = os.environ.get("WHISPER_MODEL", "base")
print(f"[Transcriber] Loading Whisper model: {MODEL_SIZE}")
_model = whisper.load_model(MODEL_SIZE)
print(f"[Transcriber] Whisper model loaded.")


def transcribe_file(file_path: str) -> str:
    """
    Transcribe an audio/video file using Whisper.

    Args:
        file_path: Absolute path to the audio/video file.

    Returns:
        Transcribed text string.
    """
    print(f"[Transcriber] Transcribing file: {file_path}")
    result = _model.transcribe(file_path)
    return result.get("text", "").strip()


def transcribe_youtube(url: str) -> str:
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

        return transcribe_file(audio_file)


def transcribe_text_passthrough(text: str) -> str:
    """
    When the user pastes text directly, no transcription needed.
    Just return the text as-is.
    """
    return text.strip()
