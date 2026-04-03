# Test script for faster-whisper integration
from faster_whisper import WhisperModel

model = WhisperModel("base", device="cpu")
segments, info = model.transcribe("test.wav")
for segment in segments:
    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
