"""Clean the matte from `hyperframes remove-background`: keep the body plus any detached
piece that is skin-coloured (a waving hand), drop everything else (red pipes, faint house
ghosts), and kill semi-transparent haze away from the kept subject.

  python refine_alpha.py IN.webm OUT.webm [--frames 60,900 --preview DIR]
"""
import argparse, subprocess, os, sys
import numpy as np, cv2

W, H = 1080, 1920


def refine(rgba):
    rgb, a = rgba[..., :3], rgba[..., 3]
    hard = (a > 127).astype(np.uint8)
    k, lab, st, _ = cv2.connectedComponentsWithStats(hard, connectivity=8)
    keep = np.zeros_like(hard)
    if k > 1:
        main = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        keep[lab == main] = 1
        ycc = cv2.cvtColor(rgb, cv2.COLOR_RGB2YCrCb)
        hue = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)[..., 0]
        # skin is orange-ish (hue < 30); pink/magenta site pipes share skin's Cr range but not its hue
        skin = (cv2.inRange(ycc, (50, 135, 80), (255, 180, 130)) > 0) & (hue < 30)
        for i in range(1, k):
            if i == main or st[i, cv2.CC_STAT_AREA] < 0.0015 * W * H:
                continue
            m = lab == i
            if skin[m].mean() > 0.45:
                keep[m] = 1
    # Saturated red objects (site pipes) that sit on the matte edge: cut them out. Lips are
    # enclosed by skin, so their surrounding ring is opaque and they are kept.
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    red = (((hsv[..., 0] <= 4) | (hsv[..., 0] >= 158)) & (hsv[..., 1] > 90) & (hsv[..., 2] > 60) & (keep > 0))
    red = cv2.morphologyEx(red.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    rk, rlab, rst, _ = cv2.connectedComponentsWithStats(red, connectivity=8)
    ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    for i in range(1, rk):
        if rst[i, cv2.CC_STAT_AREA] < 150:
            continue
        x, y, cw, ch = rst[i, :4]
        x0, y0, x1, y1 = max(0, x - 12), max(0, y - 12), min(W, x + cw + 12), min(H, y + ch + 12)
        comp = (rlab[y0:y1, x0:x1] == i).astype(np.uint8)
        ring = cv2.dilate(comp, ker) - comp
        if ring.sum() and (a[y0:y1, x0:x1][ring > 0] < 64).mean() > 0.2:
            keep[y0:y1, x0:x1][cv2.dilate(comp, np.ones((7, 7), np.uint8)) > 0] = 0
    zone = cv2.dilate(keep, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31)))
    zone = cv2.erode(zone, np.ones((1, 1), np.uint8))
    # never re-admit removed red pixels through the dilation
    zone[(keep == 0) & red.astype(bool)] = 0
    zone = cv2.GaussianBlur(zone.astype(np.float32), (0, 0), 4)
    out = rgba.copy()
    out[..., 3] = np.clip(a.astype(np.float32) * np.clip(zone, 0, 1), 0, 255).astype(np.uint8)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--frames"); ap.add_argument("--preview")
    a = ap.parse_args()
    rd = subprocess.Popen(["ffmpeg", "-v", "error", "-c:v", "libvpx-vp9", "-i", a.inp, "-f", "rawvideo",
                           "-pix_fmt", "rgba", "-"], stdout=subprocess.PIPE)
    want = set(int(x) for x in a.frames.split(",")) if a.frames else None
    wr = None
    if not want:
        wr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                               "-r", "30", "-i", "-", "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-crf", "18",
                               "-b:v", "0", "-g", "15", "-auto-alt-ref", "0", "-row-mt", "1", "-cpu-used", "4",
                               "-deadline", "good", "-metadata:s:v:0", "alpha_mode=1", a.out], stdin=subprocess.PIPE)
    n = 0
    while True:
        buf = rd.stdout.read(W * H * 4)
        if len(buf) < W * H * 4:
            break
        fr = np.frombuffer(buf, np.uint8).reshape(H, W, 4)
        out = refine(fr)
        if want is not None:
            if n in want:
                os.makedirs(a.preview, exist_ok=True)
                green = np.zeros((H, W, 3), np.float32); green[:] = (0, 177, 64)
                def comp(x):
                    al = x[..., 3:4].astype(np.float32) / 255
                    return (x[..., :3] * al + green * (1 - al)).astype(np.uint8)
                cv2.imwrite(f"{a.preview}/a{n:05d}.png", cv2.cvtColor(np.hstack([comp(fr), comp(out)]), cv2.COLOR_RGB2BGR))
            if n >= max(want):
                break
        else:
            wr.stdin.write(out.tobytes())
        n += 1
        if n % 300 == 0:
            print(n, "frames", file=sys.stderr, flush=True)
    rd.kill()
    if wr:
        wr.stdin.close(); wr.wait()
    print("done", n, file=sys.stderr)


if __name__ == "__main__":
    main()
