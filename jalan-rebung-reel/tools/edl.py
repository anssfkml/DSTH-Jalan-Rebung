"""Edit decision list: source cuts (seconds in assets/footage.mp4) and caption groups.
Run `python3 tools/edl.py` to print the edit timeline used by index.html / compositions."""
import json
# (src_in, src_out, zoom, note)
EDL = [
    (13.52, 17.32, 1.00, "HOOK  Harga bermula dari RM505K net."),
    (17.96, 19.79, 1.12, "bulanan bermula serendah"),
    (20.10, 21.70, 1.22, "RM2.3K."),
    (1.96, 5.80, 1.00, "Sekarang saya berada dekat Jalan Rebung, Bukit Kapar."),
    (6.24, 8.66, 1.12, "Belakang saya ni ada teres dua tingkat,"),
    (10.22, 12.97, 1.00, "jangka siap Q1 2027."),
    (22.37, 23.25, 1.12, "Cashback ada,"),
    (23.82, 24.74, 1.00, "kalau nak cashback,"),
    (25.70, 26.52, 1.15, "zero deposit."),
    (28.15, 29.34, 1.00, "Freehold Malay Reserve,"),
    (29.90, 30.97, 1.12, "tanah dia besar ya,"),
    (31.53, 32.60, 1.00, "19 darab"),
    (32.94, 34.50, 1.12, "108 kaki."),
    (34.67, 36.36, 1.00, "Tanah belakang 43 kaki,"),
    (36.86, 38.67, 1.12, "4 bilik, 3 bilik air."),
    (39.24, 44.70, 1.00, "So kalau berminat, cepat-cepat contact saya sebab unit sangat dah terhad. [thumbs up]"),
]
# (text, src_start, src_end, highlighted words)
CAPS = [
    ("Harga bermula dari", 13.58, 14.85, []),
    ("RM505K NET", 14.85, 17.28, ["RM505K", "NET"]),
    ("bulanan bermula serendah", 18.00, 19.73, []),
    ("RM2.3K", 20.16, 21.64, ["RM2.3K"]),
    ("Sekarang saya berada", 2.02, 3.25, []),
    ("dekat Jalan Rebung,", 3.25, 4.65, ["Jalan", "Rebung,"]),
    ("Bukit Kapar.", 4.86, 5.75, ["Bukit", "Kapar."]),
    ("Belakang saya ni ada", 6.29, 7.35, []),
    ("teres dua tingkat,", 7.35, 8.61, ["teres", "dua", "tingkat,"]),
    ("jangka siap", 10.28, 10.95, []),
    ("Q1 2027.", 11.22, 12.91, ["Q1", "2027."]),
    ("Cashback ada,", 22.43, 23.19, ["Cashback"]),
    ("kalau nak cashback,", 23.88, 24.68, []),
    ("zero deposit.", 25.76, 26.47, ["zero", "deposit."]),
    ("Freehold Malay Reserve,", 28.21, 29.28, ["Freehold"]),
    ("tanah dia besar ya,", 29.96, 30.91, ["besar"]),
    ("19 darab", 31.59, 32.54, ["19"]),
    ("108 kaki.", 33.00, 34.44, ["108"]),
    ("Tanah belakang 43 kaki,", 34.73, 36.30, ["43"]),
    ("4 bilik,", 36.92, 37.48, ["4"]),
    ("3 bilik air.", 37.87, 38.61, ["3"]),
    ("So kalau berminat,", 39.30, 40.15, []),
    ("cepat-cepat contact saya", 40.15, 41.31, ["contact"]),
    ("sebab unit", 41.49, 42.18, []),
    ("sangat dah terhad.", 42.39, 43.31, ["terhad."]),
]

# B-roll cutaways over the voice: (asset in assets/broll, edit-time in, edit-time out, note).
# Times are given as source seconds of the face-talk take (word boundaries), mapped through the cut.
BROLL_SRC = [
    ("drone-hook", 13.52, 17.32, "HOOK aerial under the price"),
    ("drone-wide", 3.30, 5.80, "Jalan Rebung, Bukit Kapar"),
    ("row", 7.33, 8.66, "teres dua tingkat"),
    ("drone-front", 10.22, 12.97, "jangka siap Q1 2027"),
    ("drone-roofs", 31.53, 34.50, "19 darab 108 kaki"),
    ("backyard", 34.67, 36.36, "Tanah belakang 43 kaki"),
]

def timeline():
    t = 0.0; clips = []
    for i, (a, b, z, note) in enumerate(EDL):
        clips.append({"i": i, "start": round(t, 3), "dur": round(b - a, 3), "src": a, "src_out": b, "zoom": z, "note": note})
        t += b - a
    return clips, round(t, 3)

def to_edit(src, clips):
    for c in clips:
        if c["src"] - 1e-6 <= src <= c["src_out"] + 1e-6:
            return round(c["start"] + src - c["src"], 3)
    raise ValueError(src)

if __name__ == "__main__":
    clips, total = timeline()
    for c in clips:
        print(f'{c["start"]:6.2f}-{c["start"]+c["dur"]:6.2f}  src {c["src"]:5.2f}-{c["src_out"]:5.2f}  z{c["zoom"]}  {c["note"]}')
    print("TOTAL", total)
    caps = []
    for k, (txt, s, e, hl) in enumerate(CAPS):
        caps.append({"id": f"cap{k}", "text": txt, "start": to_edit(s, clips), "end": to_edit(e, clips), "hl": hl})
    for c in caps: print(f'  {c["start"]:6.2f}-{c["end"]:6.2f}  {c["text"]}')
    import os
    broll = [{"id": n, "start": to_edit(a, clips), "end": to_edit(b, clips), "note": note} for n, a, b, note in BROLL_SRC]
    for b in broll: print(f'  BROLL {b["start"]:6.2f}-{b["end"]:6.2f}  {b["id"]:12s} {b["note"]}')
    json.dump({"clips": clips, "total": total, "captions": caps, "broll": broll},
              open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "edit-timeline.json"), "w"), indent=1)
