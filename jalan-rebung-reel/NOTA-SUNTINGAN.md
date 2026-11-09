# Nota Suntingan — Teres 2 Tingkat, Jalan Rebung (Bukit Kapar)

Sumber: satu take selfie 44.8s (iPhone, potret). Hasil suntingan: **32.7s**.

## Transkrip asal (Whisper large-v3, disemak dua kali)

| Masa | Ucapan |
|---|---|
| 0.0–1.1 | *(senyap)* |
| 1.1–1.6 | Okay guys, |
| 2.0–5.8 | sekarang saya berada dekat Jalan Rebung, Bukit Kapar. |
| 6.3–13.0 | Belakang saya ni ada teres dua tingkat yang dah nak siap, jangka siap Q1 2027. |
| 13.6–17.3 | Harga bermula dari RM505K net. |
| 17.8–21.6 | So bulanan bermula serendah RM2.3K. |
| 22.4–26.5 | Cashback ada, kalau nak cashback, *err…* zero deposit. |
| 27.3–34.4 | So, freehold Malay Reserve, tanah dia besar ya, 19 darab 108 kaki. |
| 34.7–38.6 | Tanah belakang 43 kaki, 4 bilik, 3 bilik air. |
| 39.3–43.3 | So kalau berminat, cepat-cepat contact saya sebab unit sangat dah terhad. |
| 43.3–44.7 | *(senyum + thumbs up)* |

## Apa yang dibuang
- Senyap di awal + "Okay guys" (permulaan lemah)
- "yang dah nak siap" (berulang dengan "jangka siap")
- "So" sebelum "bulanan" dan "freehold"
- "Err…" sebelum "zero deposit"
- Semua jeda panjang (0.4–0.7s) antara ayat

## Struktur baharu
| Masa | Babak | Grafik |
|---|---|---|
| 0.0–7.2 | **HOOK**: harga + bulanan dipindah ke depan | Tajuk + RM505K (ada dari frame 0), cop NET, kaunter RM2.3K bergulung |
| 7.2–16.2 | Lokasi + rumah | Pin peta, kad Teres 2 Tingkat, garis masa Q1 2027 |
| 16.2–21.1 | Tawaran | Chip Cashback / Zero Deposit, FREEHOLD + Malay Reserve |
| 21.1–27.3 | Tanah + bilik | Lot dilukis ikut skala 19' × 108', chip tanah belakang 43 kaki, ikon 4 bilik / 3 bilik air |
| 27.3–32.7 | CTA | BERMINAT?, butang Contact Saya, cop UNIT SANGAT TERHAD, tutup dengan thumbs up |

## Hook versi 3: tanah belakang 43'
Hook baharu (0–2.76s): *"Tanah dia besar ya, tanah belakang 43 kaki."* dipindah ke depan.
- 0–1.07: shot backyard (tangan tunjuk tanah belakang) + teks besar TANAH BELAKANG **43'** KAKI dari frame 0, cop BESAR! pada "besar".
  (Muka awak pada ayat ni tunduk/tangan dekat muka, jadi tak dipakai sebagai frame pertama.)
- 1.07–2.76: drone belakang rumah (DJI 52–56s, 2x), jalur tanah belakang disorot kuning + anak panah + label **43 KAKI** pada "43".
- Kemudian harga RM505K (drone depan) seperti sebelum ini.
Ayat "tanah dia besar ya" dan "tanah belakang 43 kaki" dibuang dari bahagian tengah supaya tak berulang;
kad keluasan tanah masih tunjuk chip "+ TANAH BELAKANG 43 KAKI" sebagai peringatan.

## B-roll (versi 2 — fail baharu dari Google Drive)
Sumber dalam folder Drive "DSTH Jalan Rebung": `face talk` (sama seperti sebelum ini), `DJI_0082.MP4` (drone 4K, 92s),
`overview` (6.4s), `2 overview` (24.6s), `backyard` (11.1s).

Transkrip b-roll: `overview` dan `2 overview` tiada ucapan (hanya bunyi angin). `backyard` ada suara perlahan
("…mana dia, panjangnya 43 kaki…") tapi terlalu perlahan dan bertindih dengan face talk — audio tidak dipakai, gambar sahaja.

| Masa edit | Shot | Ucapan di atasnya |
|---|---|---|
| 0.00–3.80 | Drone orbit dari depan rumah (2x) | **HOOK** "Harga bermula dari RM505K net" |
| 8.57–11.07 | Drone wide, deretan penuh + bukit (2x) | "…Jalan Rebung, Bukit Kapar" |
| 12.16–13.49 | Ground-level deretan gable (crop atas, lopak lumpur dibuang) | "teres dua tingkat" |
| 13.49–16.24 | Drone depan rumah hampir siap (2x) | "jangka siap Q1 2027" |
| 21.12–23.75 | Drone sudut tinggi sepanjang deretan (2x) | "19 darab 108 kaki" |
| 23.75–25.44 | Backyard: tangan tunjuk tanah belakang | "Tanah belakang 43 kaki" |

Tidak dipakai: `2 overview` (banyak sampah binaan di depan), drone 60–92s (blok yang belum siap).
Setiap b-roll masuk dengan punch-in (1.16 → 1.0) + whoosh, kemudian push perlahan.
Semua teks diperiksa dalam TikTok safe zone (atas 150px, bawah 420px, lajur ikon kanan 120px).
Potong semula: `python3 tools/broll.py` (perlu `source/drive/`), senarai shot dalam `BROLL_SRC` di `tools/edl.py`.

## Kecantikan muka (glow + gigi)
- `tools/beauty.py` jejak muka setiap frame (MediaPipe Face Landmarker) dan **hanya dalam kawasan muka**:
  licinkan kulit (edge-preserving, tekstur dikekalkan ~40%), tambah glow lembut pada kulit,
  dan dalam garis bibir dalam: kurangkan kuning gigi + ratakan tona gigi yang lebih gelap.
  Mata, kening, bibir, cermin mata, tudung dan latar tidak disentuh.
- Grade seluruh frame: Hyperframes `media-treatment` Natural Portrait (`skin-soft`) + bloom sangat ringan
  (`tools/grade.json`). Bloom kuat ditolak sebab langit jadi putih berkabus dan rumah hilang detail.
- Kekuatan boleh diubah di atas `tools/beauty.py` (`SMOOTH`, `GLOW`, `TEETH_YELLOW`, `TEETH_EVEN`).

## Greenscreen (latar diganti)
- Latar: rakaman kamera belakang berasingan (`assets/background.mp4` = bahagian 20.8–46s, tanpa audio),
  dimainkan 0.77x. Zoom 2.1x (titik 15% dari atas) dipilih secara automatik: bumbung di belakang kepala,
  dan tangan dalam rakaman itu sama ada di luar frame atau tersorok di belakang badan awak.
- Saiz awak: 80% (berlabuh di bawah), tepi kiri/kanan dilembutkan.
- Awak: `npx hyperframes remove-background` → dibersihkan oleh `tools/refine_alpha.py` (buang paip merah
  dan bayang rumah, kekalkan tangan yang terpisah) → `assets/subject.webm` (VP9 + alpha).
- Suara: dari kamera depan (`assets/voice.m4a`), dipotong sama seperti gambar.

Zoom berselang (1.0 / 1.12 / 1.22) pada setiap potongan untuk sembunyikan jump cut.
Kesan bunyi (whoosh, pop, click, impact) dari pustaka Pixabay yang dibundel — lihat `assets/sfx/CREDITS.md`.

## Cara ubah
- Potongan & caption: `tools/edl.py` → `python3 tools/edl.py && python3 tools/build.py`
- Grafik setiap babak: `compositions/*.html`
- Preview: `npx hyperframes preview` · Draf preview: `npx hyperframes render -q draft -o preview/draf.mp4` · Semak: `npx hyperframes check` · Render final: `npx hyperframes render`
