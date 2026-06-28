"""Day 1: record audio from mic, transcribe with Whisper, print the text."""
import time
import sounddevice as sd
import scipy.io.wavfile as wavfile
import whisper

# === Settings ===
SAMPLE_RATE = 16000      # Whisper's preferred sample rate
DURATION = 5             # Seconds to record
OUTPUT_FILE = "test_recording.wav"
MODEL_NAME = "small.en"  # English-only Whisper model — fast and accurate enough


def record_audio(duration: int, sample_rate: int, output_file: str) -> None:
    """Record audio from the default microphone and save as WAV."""
    import time
    print(f"\nRecording will start in 3 seconds...")
    time.sleep(1); print("3...")
    time.sleep(1); print("2...")
    time.sleep(1); print("1...")
    # Start recording slightly BEFORE 'GO' so bluetooth latency doesn't clip the first word
    audio = sd.rec(int((duration + 1) * sample_rate), samplerate=sample_rate, channels=1, dtype="int16", device=2)
    time.sleep(0.5)
    print("GO")
    sd.wait()  # Block until recording finishes
    print("Recording done.")
    wavfile.write(output_file, sample_rate, audio)


def transcribe(audio_path: str, model_name: str) -> str:
    """Load the Whisper model and transcribe the file."""
    print(f"\nLoading Whisper model '{model_name}' (first time downloads ~500MB)...")
    t0 = time.time()
    model = whisper.load_model(model_name)
    print(f"Model loaded in {time.time() - t0:.1f}s.")

    print("Transcribing...")
    t1 = time.time()
    result = model.transcribe(audio_path, fp16=False)
    print(f"Transcription done in {time.time() - t1:.1f}s.")
    return result["text"].strip()


if __name__ == "__main__":
    record_audio(DURATION, SAMPLE_RATE, OUTPUT_FILE)
    text = transcribe(OUTPUT_FILE, MODEL_NAME)
    print("\n" + "=" * 50)
    print("WHAT YOU SAID:")
    print(text)
    print("=" * 50)