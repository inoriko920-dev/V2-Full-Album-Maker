# Full Album Maker

Aplikasi pembuat video full-album berbasis Windows, dengan editor media/timeline, rendering FFmpeg dan dukungan AI opsional. Repository **V2-Full-Album-Maker** kini memiliki source code, pengujian otomatis, skrip build Windows, dan rilis portable yang telah diverifikasi.

> Repository ini adalah pengembangan V2. Repository asli `inoriko920-dev/Full-Album-Maker` tidak diubah.

## Download — versi stabil terbaru

**Full Album Maker v2.0.3 — Windows portable** (8 Oktober 2026)

- [Download ZIP Windows portable v2.0.3](https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/download/v2.0.3/Full-Album-Maker-v2.0.3-Windows-Portable.zip)
- [Download SHA256SUMS.txt](https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/download/v2.0.3/SHA256SUMS.txt)
- [Catatan rilis v2.0.3](docs/RELEASE_NOTES_v2.0.3.md)
- [Semua GitHub Releases](https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases)

Identitas ZIP yang dipublikasikan dan diuji:

| Properti | Nilai |
| --- | --- |
| Nama | `Full-Album-Maker-v2.0.3-Windows-Portable.zip` |
| Ukuran | **189.599.847 byte** |
| SHA-256 | `b2b2a3c7bac889f63ca2d84ffc65b035533ab22b22dc5c31e22bd1d1ae7247f0` |
| Tag | `v2.0.3` |
| Commit sumber rilis | `ee61ca0af5d15cdc51af91ad48e05bc2b641f49d` |

**Cara menggunakan:** unduh ZIP, ekstrak ke folder yang dapat ditulis di Windows 11, lalu jalankan `Full Album Maker.exe` dari hasil ekstraksi. Jangan menjalankan executable langsung dari dalam ZIP. Simpan versi lama di folder terpisah jika ingin rollback. Paket portable sudah membundel FFmpeg/FFprobe dan dependensi runtime; pengguna tidak perlu memasang Python secara global untuk menjalankannya. Fitur AI yang menggunakan layanan eksternal tetap memerlukan konfigurasi provider yang sesuai.

Untuk memeriksa ZIP di PowerShell:

```powershell
Get-FileHash .\Full-Album-Maker-v2.0.3-Windows-Portable.zip -Algorithm SHA256
```

Nilai yang muncul harus cocok dengan SHA-256 pada tabel atau `SHA256SUMS.txt`. Hentikan penggunaan file jika tidak cocok.

## Source code dan pengujian

Struktur utama:

- `src/full_album_maker/` — source aplikasi dan layanan media.
- `tests/` — regression test otomatis.
- `build/` — manifest, dependency lock, skrip build dan pemeriksaan portable.
- `.github/workflows/` — GitHub Actions Windows CI dan quality gate rilis.
- `docs/` — dokumentasi perencanaan, implementasi, bukti pengujian, dan handoff AI.

Bagi developer yang ingin menjalankan tes dari source:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Untuk menghasilkan paket portable sendiri di Windows:

```powershell
.\build\build_portable.ps1
```

Build memerlukan lingkungan Windows dan koneksi untuk mengambil dependensi serta FFmpeg/font yang dipin dan diverifikasi checksum-nya. Versi Python **3.12.10** dipakai oleh quality gate rilis; untuk reproduksi paket resmi, ikuti pin lengkap pada `build/release_manifest.json` dan `build/requirements-windows.lock`. **Build lokal baru tidak otomatis identik byte-per-byte dengan ZIP yang telah dirilis.**

## Jaminan rilis dan riwayat

Rilis v2.0.3 telah melewati dua gate terpisah: [Q4 — Windows build/test/freeze](docs/implementation/Q4_V2_0_3_EVIDENCE.md) dan [Q5 — publikasi ZIP Q4 tanpa rebuild](docs/implementation/Q5_V2_0_3_EVIDENCE.md). Q5 mengunduh dan memeriksa ulang aset publikasi, termasuk ukuran, hash dan target commit tag. Rilis sebelumnya `v2.0.2`, `v2.0.1` dan `v2.0.0` tetap tersedia sebagai pilihan rollback.

Untuk melanjutkan pekerjaan di sesi atau AI lain, baca [AI handoff](docs/governance/AI_HANDOFF.md), [status proyek](docs/governance/PROJECT_STATUS.md), dan dokumen keputusan yang dirujuk oleh keduanya. Setiap perubahan executable harus dibuat pada branch terpisah, melewati CI, dan dirilis dengan versi serta Q4/Q5 baru; jangan mengganti ZIP/tag stabil yang sudah dipublikasikan.

## Catatan arsip pemulihan historis

Repository ini **berawal** dari penyelamatan arsip portable saat akses repository lama terganggu. Saat itu arsip build tersedia lebih dulu daripada keseluruhan source yang sekarang telah dikembangkan pada V2. Untuk menjaga provenance, checksum historisnya tetap dicatat di sini:

- SHA-256 arsip luar pemulihan: `eadd0453d2e4b7d253e5cfd4e0b79ee07dccd0fd8df71d028e2c31b63ec7523d`.
- SHA-256 ZIP portable v1.4.1 di dalamnya: `b0d571692f925296022f146c39dce388b4717a43417e7f80132bd3aa52a9d853`.

Arsip lama adalah bahan historis/pemulihan, **bukan** versi download terbaru dan bukan pengganti repository source V2. Jangan menghapus cadangan asli hanya karena versi baru telah diterbitkan.

## Lisensi

Source repository berlisensi [MIT](LICENSE). FFmpeg, font dan komponen pihak ketiga mengikuti lisensinya masing-masing, yang dijelaskan dalam [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
