# Nota Suntingan — Teres 2 Tingkat, Jalan Rebung (Bukit Kapah)

Sumber: satu take selfie 44.8s (iPhone, potret). Hasil suntingan: **32.7s**.

## Transkrip asal (Whisper large-v3, disemak dua kali)

| Masa | Ucapan |
|---|---|
| 0.0–1.1 | *(senyap)* |
| 1.1–1.6 | Okay guys, |
| 2.0–5.8 | sekarang saya berada dekat Jalan Rebung, Bukit Kapah. |
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

Zoom berselang (1.0 / 1.12 / 1.22) pada setiap potongan untuk sembunyikan jump cut.
Kesan bunyi (whoosh, pop, click, impact) dari pustaka Pixabay yang dibundel — lihat `assets/sfx/CREDITS.md`.

## Cara ubah
- Potongan & caption: `tools/edl.py` → `python3 tools/edl.py && python3 tools/build.py`
- Grafik setiap babak: `compositions/*.html`
- Preview: `npx hyperframes preview` · Semak: `npx hyperframes check` · Render final: `npx hyperframes render`
