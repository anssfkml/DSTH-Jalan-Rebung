"""Cuts the b-roll shots out of the raw camera files into assets/broll/*.mp4 (1080x1920, muted,
pre-sped, short GOP so the preview seeks cleanly). The raw files live in source/drive/ (git-ignored,
from the Google Drive folder "DSTH Jalan Rebung").

    python3 tools/broll.py
"""
import os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "source", "drive", "DSTH Jalan Rebung")
OUT = os.path.join(ROOT, "assets", "broll")

# name: (source file, in, out, speed, note)
SHOTS = {
    "backyard":    ("Dsth jalan rebung backyard", 1.9, 3.1, 1.0, "hand points across the back land (hook frame 0)"),
    "drone-back":  ("DJI_0082.MP4", 52.0, 56.0, 2.0, "rear of the row, the cleared back land in front"),
    "drone-hook":  ("DJI_0082.MP4", 13.0, 21.0, 2.0, "orbit off the front facades along the row"),
    "drone-wide":  ("DJI_0082.MP4", 40.0, 48.0, 2.0, "sweep to the whole row with the hills behind"),
    "row":         ("Dsth jalan rebung overview", 0.0, 2.0, 1.25, "ground level, row of gables in perspective"),
    "drone-front": ("DJI_0082.MP4", 2.0, 8.0, 2.0, "front facades, near-finished"),
    "drone-roofs": ("DJI_0082.MP4", 26.0, 34.0, 2.0, "high angle down the length of the row"),
}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, (f, a, b, speed, _note) in SHOTS.items():
        dst = os.path.join(OUT, f"{name}.mp4")
        vf = f"setpts=PTS/{speed},scale=1080:1920:flags=lanczos,fps=30,format=yuv420p"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-t", str(b - a),
                        "-i", os.path.join(SRC, f), "-an", "-sn", "-dn", "-map_metadata", "-1",
                        "-vf", vf, "-c:v", "libx264", "-preset", "slow", "-crf", "23", "-g", "15",
                        "-movflags", "+faststart", dst], check=True)
        print(f"{name:12s} {(b - a) / speed:5.2f}s  <- {f} {a}-{b} @{speed}x")
