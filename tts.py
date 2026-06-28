"""Text-to-speech for Jarvis using Piper."""
import os
import subprocess
import tempfile
import sounddevice as sd
import soundfile as sf

# === Config ===
PIPER_EXE = r"C:\piper\piper.exe"
VOICE_MODEL = r"C:\piper\jarvis-medium.onnx"


def speak(text: str, wait: bool = True) -> None:
    """Convert text to speech with Piper and play it.

    Args:
        text: what Jarvis should say
        wait: if True, block until playback finishes. If False, returns immediately while audio plays.
    """
    if not text or not text.strip():
        return

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav_path = f.name

    try:
        # Generate audio via Piper
        subprocess.run(
            [PIPER_EXE, "--model", VOICE_MODEL, "--output_file", wav_path],
            input=text,
            text=True,
            capture_output=True,
            check=True,
        )

        # Load and play
        audio, sample_rate = sf.read(wav_path)
        sd.play(audio, sample_rate)
        if wait:
            sd.wait()
    except subprocess.CalledProcessError as e:
        print(f"[TTS error: {e.stderr}]")
    finally:
        try:
            os.remove(wav_path)
        except OSError:
            pass