"""Day 1: record audio from mic, transcribe with Whisper, print the text.

Usage:
    python voice_test.py           # defaults to small.en
    python voice_test.py -s        # small.en (fastest)
    python voice_test.py -m        # medium.en (more accurate, slower)
    python voice_test.py -l        # large (most accurate, slowest, biggest VRAM)
"""
import argparse
import time
import sounddevice as sd
import scipy.io.wavfile as wavfile
import whisper
import torch

# === Settings ===
SAMPLE_RATE = 16000
DURATION = 5
OUTPUT_FILE = "test_recording.wav"
MIC_DEVICE = 2  # Soundcore Q20i


def record_audio(duration: int, sample_rate: int, output_file: str) -> None:
    """Record audio from the default microphone and save as WAV."""
    print(f"\nRecording will start in 3 seconds...")
    time.sleep(1); print("3...")
    time.sleep(1); print("2...")
    time.sleep(1); print("1...")
    audio = sd.rec(
        int((duration + 1) * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16",
        device=MIC_DEVICE,
    )
    time.sleep(0.5)
    print("GO")
    sd.wait()
    print("Recording done.")
    wavfile.write(output_file, sample_rate, audio)


def transcribe(audio_path: str, model_name: str) -> str:
    """Load the Whisper model and transcribe the file."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\nLoading Whisper model '{model_name}' on {device.upper()}...")
    t0 = time.time()
    model = whisper.load_model(model_name, device=device)
    print(f"Model loaded in {time.time() - t0:.1f}s.")

    print("Transcribing...")
    t1 = time.time()
    use_fp16 = torch.cuda.is_available()
    result = model.transcribe(audio_path, fp16=use_fp16)
    print(f"Transcription done in {time.time() - t1:.1f}s.")
    return result["text"].strip()


def parse_args():
    parser = argparse.ArgumentParser(description="Test Whisper transcription with a chosen model.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-s", "--small", action="store_const", dest="model", const="small.en",
                       help="Use small.en (fastest, ~500MB)")
    group.add_argument("-m", "--medium", action="store_const", dest="model", const="medium.en",
                       help="Use medium.en (~1.5GB, slower but more accurate)")
    group.add_argument("-l", "--large", action="store_const", dest="model", const="large-v3",
                       help="Use large-v3 (~3GB, slowest but most accurate)")
    parser.set_defaults(model="small.en")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    record_audio(DURATION, SAMPLE_RATE, OUTPUT_FILE)
    text = transcribe(OUTPUT_FILE, args.model)
    print("\n" + "=" * 50)
    print(f"MODEL: {args.model}")
    print("WHAT YOU SAID:")
    print(text)
    print("=" * 50)