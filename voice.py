"""Voice input — record from mic until silence, transcribe with Whisper."""
import time
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wavfile
import whisper
import torch

# === Config ===
SAMPLE_RATE = 16000
TEMP_FILE = "voice_input.wav"
MODEL_NAME = "small.en"
MIC_DEVICE = 2  # Soundcore Q20i

# VAD settings
CHUNK_DURATION = 0.1          # Listen in 100ms chunks
SILENCE_DURATION = 2.0        # Stop after 2 seconds of silence
SILENCE_THRESHOLD = 500       # Below this RMS level = silence (for int16 audio)
MAX_DURATION = 30             # Hard cap so it can't record forever
MIN_DURATION = 1.0            # Don't stop in the first 1 second (gives you time to start talking)


_model = None


def load_model():
    """Load Whisper once and cache it."""
    global _model
    if _model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"  Loading Whisper '{MODEL_NAME}' on {device.upper()} (one-time)...")
        t0 = time.time()
        _model = whisper.load_model(MODEL_NAME, device=device)
        print(f"  Whisper ready in {time.time() - t0:.1f}s.\n")
    return _model


def _rms(chunk: np.ndarray) -> float:
    """Root mean square — a measure of how loud the chunk is."""
    return float(np.sqrt(np.mean(chunk.astype(np.float64) ** 2)))


def listen() -> str:
    """Record from mic until silence detected, transcribe, return text."""
    model = load_model()

    chunk_samples = int(CHUNK_DURATION * SAMPLE_RATE)
    silence_chunks_needed = int(SILENCE_DURATION / CHUNK_DURATION)
    max_chunks = int(MAX_DURATION / CHUNK_DURATION)
    min_chunks = int(MIN_DURATION / CHUNK_DURATION)

    print(f"\n  Listening — speak now (stops {SILENCE_DURATION:.0f}s after you finish)...")

    recorded_chunks = []
    silent_chunks_in_a_row = 0

    # Open a continuous input stream
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
        device=MIC_DEVICE,
        blocksize=chunk_samples,
    ) as stream:
        for i in range(max_chunks):
            chunk, _ = stream.read(chunk_samples)
            chunk = chunk.flatten()
            recorded_chunks.append(chunk)

            level = _rms(chunk)

            # Don't start the silence-counter until we've recorded the minimum duration
            if i < min_chunks:
                continue

            if level < SILENCE_THRESHOLD:
                silent_chunks_in_a_row += 1
                if silent_chunks_in_a_row >= silence_chunks_needed:
                    break
            else:
                silent_chunks_in_a_row = 0

    print(f"  Done. ({len(recorded_chunks) * CHUNK_DURATION:.1f}s recorded)")

    # Stitch chunks back together and save
    audio = np.concatenate(recorded_chunks)
    wavfile.write(TEMP_FILE, SAMPLE_RATE, audio)

    # Transcribe
    use_fp16 = torch.cuda.is_available()
    t0 = time.time()
    result = model.transcribe(TEMP_FILE, fp16=use_fp16)
    elapsed = time.time() - t0
    text = result["text"].strip()

    # Filter Whisper hallucinations on silence
    GARBAGE = {"You", "you", "Thank you.", "Thanks for watching."}
    if not text or text in GARBAGE:
        print(f"  [no speech detected — {elapsed:.1f}s]")
        return ""

    print(f"  [transcribed in {elapsed:.1f}s]")
    return text