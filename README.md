# LectureMind

LectureMind is a modern full-stack web application designed to transcribe and summarize lectures effortlessly. Powered by OpenAI's Whisper model and LSA summarization, it features a sleek UI reminiscent of Notta AI, robust Firebase Authentication, and Firestore database integration.

## Features

- **Multi-Source Support:** Upload audio/video files, paste text directly, or provide a YouTube URL.
- **Accurate Transcription:** Uses OpenAI's `whisper` model to transcribe spoken word to text.
- **Smart Summarization:** Extracts 3–5 (or more) key sentences using LSA (Latent Semantic Analysis) via the `sumy` library.
- **Adjustable Summary Lengths:** Choose between Short, Medium, or Long summaries.
- **Cloud Storage:** Stores all transcritps and summaries securely in Firebase Firestore.
- **Beautiful UI:** A dark, sleek, glass-morphism dashboard inspired by Notta.

---

## 🚀 Setup Instructions

### 1. Requirements

- **Python 3.8+**
- **FFmpeg:** Required by Whisper to process audio/video files.
  - **Mac:** `brew install ffmpeg`
  - **Ubuntu/Debian:** `sudo apt update && sudo apt install ffmpeg`
  - **Windows:** Install via `winget install ffmpeg` or download from the official site.

### 2. Firebase Setup (Crucial Step)

Because LectureMind handles user accounts and saves data over the cloud, you need a Firebase project.

#### A) Create a Firebase Project
1. Go to the [Firebase Console](https://console.firebase.google.com/).
2. Click **Add project** and follow the steps.
3. Once created, go to **Build > Authentication** and enable **Email/Password** sign-in mechanism.
4. Go to **Build > Firestore Database** and click **Create database** (Start in **Test mode** or configure basic rules that allow reads/writes for authenticated users).

#### B) Get Web SDK Config (Frontend)
1. Go to **Project Settings** (gear icon) > **General**.
2. Scroll to **Your apps**, click the web icon (`</>`), and register your app.
3. Copy the `firebaseConfig` object.
4. Open `frontend/js/firebase-config.js` and replace the placeholder values.

#### C) Get Service Account Key (Backend)
1. Go to **Project Settings** > **Service accounts**.
2. Click **Generate new private key**.
3. Save the downloaded JSON file.
4. Rename the file to `serviceAccountKey.json`.
5. Place it inside the `backend/` directory (`backend/serviceAccountKey.json`).

### 3. Backend Setup

1. Open a terminal and navigate to the project directory:
   ```bash
   cd "Lecture Summarizer"
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
   *Note: Whisper may take a moment to install depending on your connection.*

### 4. Running the App

The app backend will automatically serve the frontend files, meaning you only need to run one server!

1. Start the Flask server:
   ```bash
   python backend/app.py
   ```

2. Open your web browser and navigate to:
   ```text
   http://localhost:5000
   ```

### Notes & Troubleshooting
- **Whisper Model:** By default, `backend/transcriber.py` uses the `base` model. To use a more accurate (but heavier/slower) model like `small` or `medium`, change `MODEL_SIZE = os.environ.get("WHISPER_MODEL", "base")` in `transcriber.py` or set the env var before running the server.
- Ensure `ffmpeg` is successfully installed and added to your system's PATH. This is the most common cause of transcription failures.
