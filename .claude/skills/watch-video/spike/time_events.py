import os, time, sys
os.environ["HF_HUB_DISABLE_TELEMETRY"]="1"
wav=sys.argv[1]
t=time.time(); import torch, numpy as np, soundfile as sf; print("import torch", round(time.time()-t,1))
t=time.time(); from silero_vad import load_silero_vad, get_speech_timestamps; vad=load_silero_vad(); print("silero load", round(time.time()-t,1))
y,sr=sf.read(wav,dtype="float32")
t=time.time(); sp=get_speech_timestamps(torch.from_numpy(y),vad,return_seconds=True); print("silero run", round(time.time()-t,2), len(sp))
t=time.time()
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification
fe=AutoFeatureExtractor.from_pretrained("mispeech/ced-tiny",trust_remote_code=True)
m=AutoModelForAudioClassification.from_pretrained("mispeech/ced-tiny",trust_remote_code=True).eval()
print("ced load", round(time.time()-t,1))
win,hop=sr,sr//2
b=[y[i:i+win] for i in range(0,len(y)-win+1,hop)]
t=time.time()
with torch.inference_mode():
    for i in range(0,len(b),64):
        x=fe(b[i:i+64],sampling_rate=sr,return_tensors="pt"); m(**x).logits
print("ced run (cpu)", round(time.time()-t,2), len(b))
print("torch threads", torch.get_num_threads())
