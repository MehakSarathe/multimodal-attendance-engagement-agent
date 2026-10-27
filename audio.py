import io
import wave
import numpy as np

def analyze_wav(raw_bytes, segment_seconds=1):
    """Calculate sound energy (RMS) per segment from a WAV file."""
    with wave.open(io.BytesIO(raw_bytes), "rb") as wav:
        channels = wav.getnchannels()
        width = wav.getsampwidth()
        rate = wav.getframerate()
        nframes = wav.getnframes()
        raw = wav.readframes(nframes)
    dtype_map = {1: np.uint8, 2: np.int16, 4: np.int32}
    if width not in dtype_map:
        raise ValueError("Unsupported WAV sample width.")
    signal = np.frombuffer(raw, dtype=dtype_map[width]).astype(np.float64)
    if width == 1:
        signal -= 128
    if channels > 1:
        usable = len(signal) - len(signal) % channels
        signal = signal[:usable].reshape(-1, channels).mean(axis=1)
    duration = len(signal) / rate if rate else 0
    chunk_size = max(1, int(rate * segment_seconds))
    segments = []
    for start in range(0, len(signal), chunk_size):
        chunk = signal[start:start + chunk_size]
        if not len(chunk):
            continue
        rms = float(np.sqrt(np.mean(chunk ** 2)))
        segments.append({"second": len(segments) + 1, "rms_level": round(rms, 2)})
    avg = float(np.mean([s["rms_level"] for s in segments])) if segments else 0
    return {
        "method": "RMS sound-energy analysis",
        "duration_seconds": round(duration, 2),
        "sample_rate_hz": rate,
        "average_rms": round(avg, 2),
        "segments": segments,
        "limitation": "Sound energy does not identify speakers, determine what was said, or prove engagement.",
    }
