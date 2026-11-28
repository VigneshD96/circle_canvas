"""Integration spike: Parakeet (MLX) + silero-vad + CED-tiny on one wav. Prints shapes, timing, peak RSS."""
import os
import resource
import sys
import time

os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
os.environ.setdefault("PYANNOTE_METRICS_ENABLED", "0")

wav = sys.argv[1]


def rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6  # macOS reports bytes


t0 = time.time()
from parakeet_mlx import from_pretrained

m = from_pretrained("mlx-community/parakeet-tdt-0.6b-v3")
t1 = time.time()
r = m.transcribe(wav, chunk_duration=120, overlap_duration=15)
t2 = time.time()
print(f"[parakeet] load {t1 - t0:.1f}s  transcribe {t2 - t1:.1f}s  peak_rss {rss_mb():.0f} MB")
print("[parakeet] text:", r.text[:300])
toks = r.tokens
print("[parakeet] n_tokens", len(toks), "first tokens:")
for t in toks[:25]:
    print(f"   {t.start:7.2f}-{t.end:7.2f} conf={t.confidence:.2f} {t.text!r}")
print("[parakeet] sentences:")
for s in r.sentences[:12]:
    print(f"   {s.start:6.2f}-{s.end:6.2f} {s.text}")

# silero-vad
t3 = time.time()
from silero_vad import get_speech_timestamps, load_silero_vad, read_audio

vad = load_silero_vad()
audio = read_audio(wav, sampling_rate=16000)
speech = get_speech_timestamps(audio, vad, return_seconds=True)
print(f"[silero] {time.time() - t3:.1f}s  spans={len(speech)} first={speech[:4]}")

# CED-tiny
t4 = time.time()
import numpy as np
import soundfile as sf
import torch
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification

name = "mispeech/ced-tiny"
fe = AutoFeatureExtractor.from_pretrained(name, trust_remote_code=True)
model = AutoModelForAudioClassification.from_pretrained(name, trust_remote_code=True).eval()
y, sr = sf.read(wav, dtype="float32")
win, hop = sr, sr // 2
batch = [y[i:i + win] for i in range(0, max(1, len(y) - win + 1), hop)]
with torch.no_grad():
    inp = fe(batch, sampling_rate=sr, return_tensors="pt")
    logits = model(**inp).logits
print(f"[ced] {time.time() - t4:.1f}s windows={len(batch)} logits shape={tuple(logits.shape)} "
      f"min={logits.min():.3f} max={logits.max():.3f}  peak_rss {rss_mb():.0f} MB")
labels = model.config.id2label
want = [k for k, v in labels.items() if v.lower() in ("speech", "laughter", "applause", "music", "silence", "male speech, man speaking", "female speech, woman speaking")]
print("[ced] label ids:", {k: labels[k] for k in want})
for wi in range(0, len(batch), max(1, len(batch) // 6)):
    print(f"   win {wi * 0.5:5.1f}s", {labels[k]: round(float(logits[wi, k]), 3) for k in want})
