"""Face-only retouch layer: tracks the face with MediaPipe Face Landmarker and, inside
the face only, (1) smooths skin with an edge-preserving filter while keeping texture,
(2) adds a soft skin glow, (3) takes the yellow out of the teeth inside the inner-lip
outline. Everything outside the face is passed through untouched.

  python beauty.py IN.mp4 OUT.mp4 --model face_landmarker.task [--frames 0,300] [--preview DIR]
  python beauty.py RAW.mp4 OUT.webm --model ... --alpha-from assets/subject.webm
      (re-retouch the presenter from the raw take, keep the existing cutout's matte frame for frame)

Needs: mediapipe, opencv-python-headless, numpy, ffmpeg on PATH.
"""
import argparse, subprocess, os, sys
import numpy as np, cv2
import mediapipe as mp

# Face Mesh landmark loops (canonical 468-point topology).
FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377,
             152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
LEFT_EYE = [263, 249, 390, 373, 374, 380, 381, 382, 362, 398, 384, 385, 386, 387, 388, 466]
RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
LEFT_BROW = [276, 283, 282, 295, 285, 300, 293, 334, 296, 336]
RIGHT_BROW = [46, 53, 52, 65, 55, 70, 63, 105, 66, 107]
LIPS_OUTER = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 409, 270, 269, 267, 0, 37, 39, 40, 185]
LIPS_INNER = [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308, 415, 310, 311, 312, 13, 82, 81, 80, 191]

# Strengths (kept natural on purpose)
SMOOTH = 0.6      # share of the smoothed skin in the mix
GLOW = 0.34       # soft screen glow on skin (v1 was 0.16; asked for more glow)
GLOW_LIFT = 7.0   # extra L* on skin, radiance (0-255 scale)
GLOW_WARM = 2.0   # nudge skin a touch warmer (b*) so the lift reads healthy, not grey
TEETH_YELLOW = 0.62  # fraction of b* (yellow) removed from teeth
TEETH_WARM_FLOOR = 131.0  # keep a hint of natural warmth: never push teeth b* below this (128 = neutral)
TEETH_EVEN = 0.5     # pull darker (greyish) teeth toward the brighter ones
TEETH_LIFT = 8.0     # L* lift on teeth (0-255 scale)
TEETH_L_CAP = 232.0  # no paper-white teeth


def poly(lm, idx, w, h, scale=1.0, cx=None, cy=None):
    pts = np.array([[lm[i].x * w, lm[i].y * h] for i in idx], np.float32)
    if scale != 1.0:
        c = pts.mean(0) if cx is None else np.array([cx, cy])
        pts = (pts - c) * scale + c
    return pts.astype(np.int32)


def process(frame, lm):
    h, w = frame.shape[:2]
    oval = poly(lm, FACE_OVAL, w, h)
    x0, y0, bw, bh = cv2.boundingRect(oval)
    pad = int(0.12 * bw)
    x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
    x1, y1 = min(w, x0 + bw + 2 * pad), min(h, y0 + bh + 2 * pad)
    crop = frame[y0:y1, x0:x1].copy()
    ch, cw = crop.shape[:2]
    off = np.array([x0, y0])

    def cpoly(idx, scale=1.0):
        return poly(lm, idx, w, h, scale) - off

    # ---- skin mask: face oval minus eyes, brows, lips; gated by skin colour ----
    m = np.zeros((ch, cw), np.uint8)
    cv2.fillPoly(m, [cpoly(FACE_OVAL, 0.97)], 255)
    for idx, s in ((LEFT_EYE, 1.5), (RIGHT_EYE, 1.5), (LEFT_BROW, 1.25), (RIGHT_BROW, 1.25), (LIPS_OUTER, 1.12)):
        cv2.fillPoly(m, [cpoly(idx, s)], 0)
    ycc = cv2.cvtColor(crop, cv2.COLOR_RGB2YCrCb)
    skin = cv2.inRange(ycc, (40, 133, 77), (255, 178, 133))
    skin = cv2.GaussianBlur(skin, (0, 0), 3)
    feather = max(3, bw // 40)
    m = cv2.GaussianBlur(m, (0, 0), feather)
    mask = (m.astype(np.float32) / 255) * (skin.astype(np.float32) / 255)
    mask = mask[..., None]

    # ---- smoothing (edge-preserving; texture kept by mixing) ----
    d = max(5, bw // 60) | 1
    sm = cv2.bilateralFilter(crop, d, 28, d)
    sm = cv2.bilateralFilter(sm, d, 22, d)
    f = crop.astype(np.float32)
    out = f * (1 - SMOOTH * mask) + sm.astype(np.float32) * (SMOOTH * mask)

    # ---- glow: screen a soft blurred copy over the skin ----
    blur = cv2.GaussianBlur(out, (0, 0), max(6, bw // 18))
    screen = 255 - (255 - out) * (255 - blur) / 255
    out = out * (1 - GLOW * mask) + screen * (GLOW * mask)
    lab = cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
    lab[..., 0] += GLOW_LIFT * mask[..., 0]
    lab[..., 2] += GLOW_WARM * mask[..., 0]
    out = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB).astype(np.float32)

    # ---- teeth: inside the inner-lip outline, bright + low-chroma pixels only ----
    mouth = np.zeros((ch, cw), np.uint8)
    cv2.fillPoly(mouth, [cpoly(LIPS_INNER, 0.96)], 255)
    if mouth.any():
        lab = cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
        L, A, B = lab[..., 0], lab[..., 1], lab[..., 2]
        # teeth: brighter than lips/tongue, not red
        inside = mouth > 127
        tmask = ((L > 88) & (A < 148)).astype(np.float32) * (mouth.astype(np.float32) / 255)
        tmask = cv2.GaussianBlur(tmask, (0, 0), 1.5)
        bright = L[inside & (L > 120) & (A < 148)]
        if bright.size > 30:
            target = float(np.percentile(bright, 60))
            L[:] = L + np.maximum(target - L, 0) * TEETH_EVEN * tmask
        B[:] = np.where(B > TEETH_WARM_FLOOR, B - (B - TEETH_WARM_FLOOR) * TEETH_YELLOW * tmask * 1.0, B)
        A[:] = A - np.maximum(A - 128, 0) * 0.25 * tmask
        L[:] = np.minimum(L + TEETH_LIFT * tmask, np.maximum(L, TEETH_L_CAP))
        out = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB).astype(np.float32)

    frame = frame.copy()
    frame[y0:y1, x0:x1] = np.clip(out, 0, 255).astype(np.uint8)
    return frame


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--model", required=True)
    ap.add_argument("--frames", help="only these frame numbers, write PNG before/after to --preview")
    ap.add_argument("--preview")
    ap.add_argument("--alpha-from", help="VP9+alpha cutout whose matte is reused; output becomes VP9+alpha WebM")
    a = ap.parse_args()
    W, H = 1080, 1920
    fps = 30
    BaseOptions = mp.tasks.BaseOptions
    opts = mp.tasks.vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=a.model),
        running_mode=mp.tasks.vision.RunningMode.VIDEO, num_faces=1,
        min_face_detection_confidence=0.4, min_tracking_confidence=0.4)
    lmk = mp.tasks.vision.FaceLandmarker.create_from_options(opts)
    rd = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.inp, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                          stdout=subprocess.PIPE)
    want = set(int(x) for x in a.frames.split(",")) if a.frames else None
    wr = None
    ard = None
    if a.alpha_from and not want:
        ard = subprocess.Popen(["ffmpeg", "-v", "error", "-c:v", "libvpx-vp9", "-i", a.alpha_from, "-f", "rawvideo",
                                "-pix_fmt", "rgba", "-"], stdout=subprocess.PIPE)
        wr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                               "-r", str(fps), "-i", "-", "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-crf", "30",
                               "-b:v", "0", "-row-mt", "1", "-deadline", "good", "-cpu-used", "4", "-g", "15",
                               "-auto-alt-ref", "0", "-metadata:s:v:0", "alpha_mode=1", a.out], stdin=subprocess.PIPE)
    elif not want:
        wr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                               "-r", str(fps), "-i", "-", "-i", a.inp, "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
                               "-preset", "medium", "-crf", "18", "-g", "15", "-keyint_min", "15", "-pix_fmt", "yuv420p",
                               "-c:a", "copy", "-movflags", "+faststart", "-shortest", a.out], stdin=subprocess.PIPE)
    n = 0; miss = 0
    while True:
        buf = rd.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        small = cv2.resize(fr, (W // 2, H // 2), interpolation=cv2.INTER_AREA)
        res = lmk.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(small)),
                                   int(n * 1000 / fps))
        if res.face_landmarks:
            outf = process(fr, res.face_landmarks[0])
        else:
            outf = fr; miss += 1
        if want is not None:
            if n in want:
                os.makedirs(a.preview, exist_ok=True)
                cv2.imwrite(f"{a.preview}/f{n:05d}.png", cv2.cvtColor(np.hstack([fr, outf]), cv2.COLOR_RGB2BGR))
            if n >= max(want):
                break
        elif ard is not None:
            abuf = ard.stdout.read(W * H * 4)
            if len(abuf) < W * H * 4:
                break
            alpha = np.frombuffer(abuf, np.uint8).reshape(H, W, 4)[..., 3:]
            wr.stdin.write(np.concatenate([outf, alpha], axis=2).tobytes())
        else:
            wr.stdin.write(outf.tobytes())
        n += 1
        if n % 150 == 0:
            print(f"{n} frames, no-face {miss}", file=sys.stderr, flush=True)
    rd.kill()
    if wr:
        wr.stdin.close(); wr.wait()
    print(f"done {n} frames, no-face {miss}", file=sys.stderr)


if __name__ == "__main__":
    main()
