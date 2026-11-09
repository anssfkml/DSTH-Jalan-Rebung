"""Voice clean-up for assets/voice.m4a: DeepFilterNet3 removes the construction-site noise,
then EQ + compression + loudness normalise so the voice sits up front.

    python3 tools/denoise.py IN_AUDIO OUT.m4a

Needs: deepfilternet (+ CPU torch/torchaudio), soundfile, ffmpeg.
"""
import sys, types, subprocess, tempfile, os
import numpy as np, soundfile as sf, torch

# deepfilternet 0.5 imports a torchaudio module removed in torchaudio 2.x; it is only used for typing.
_m = types.ModuleType("torchaudio.backend.common"); _m.AudioMetaData = object
sys.modules.setdefault("torchaudio.backend", types.ModuleType("torchaudio.backend"))
sys.modules["torchaudio.backend.common"] = _m
from df.enhance import enhance, init_df  # noqa: E402

ATTEN_LIMIT_DB = 30   # cap the noise removal so the voice keeps its body (no underwater sound)

src, dst = sys.argv[1], sys.argv[2]
tmp = tempfile.mkdtemp()
raw = os.path.join(tmp, "in.wav"); clean = os.path.join(tmp, "clean.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-ac", "1", "-ar", "48000", raw], check=True)
model, state, _ = init_df(os.path.expanduser("~/.cache/DeepFilterNet/DeepFilterNet3"))  # from raw.githubusercontent.com/Rikorose/DeepFilterNet/main/models/DeepFilterNet3.zip
x, sr = sf.read(raw, dtype="float32")
y = enhance(model, state, torch.from_numpy(x)[None], atten_lim_db=ATTEN_LIMIT_DB)[0].numpy()
sf.write(clean, y, sr)
# high-pass rumble, take a little mud out, lift presence, gentle compression, then -12 LUFS / -1 dBTP.
chain = ("highpass=f=85,equalizer=f=280:t=q:w=1.2:g=-2.5,equalizer=f=3200:t=q:w=1.0:g=3,"
         "equalizer=f=9000:t=q:w=1.0:g=1.5,"
         "acompressor=threshold=-24dB:ratio=3:attack=8:release=120:makeup=4,"
         "loudnorm=I=-12:TP=-1.0:LRA=7")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", clean, "-af", chain, "-ar", "48000", "-ac", "2",
                "-c:a", "aac", "-b:a", "192k", dst], check=True)
print("wrote", dst)
