## Ringkasan perubahan

Jelaskan apa yang berubah dan mengapa perubahan ini diperlukan.

## Scope

- [ ] Perubahan ini tidak mengubah stable asset/tag yang sudah dipublikasikan.
- [ ] Jika ini bug fix untuk v2.0.0, target versi berikutnya adalah patch baru (mis. v2.0.1), bukan mengganti asset v2.0.0.
- [ ] Tidak ada secret/API key yang ditambahkan ke repo.
- [ ] Perubahan runtime/build/release memiliki test atau evidence yang relevan.

## Validasi

- [ ] Test yang relevan sudah PASS.
- [ ] Jika menyentuh Windows portable/build/release, workflow `Build Windows Portable` harus PASS.
- [ ] Jika menyentuh release metadata, `build/release_manifest.json`, notices, version, checksum, dan release notes tetap konsisten.
- [ ] Jika menyentuh FFmpeg/preview/render, parity dan real-FFmpeg evidence tidak diregresikan.

## Release safety

Stable v2.0.0 adalah immutable reference:
- tag: `v2.0.0`
- candidate: `d2ce2ccac62cdcd8994a38251a5b547c8460421e`
- ZIP SHA-256: `4c0f2205a0a0a77d3da819ca11e4a6e57298f2003a20f132533a1b29760280ad`

Jangan retarget tag atau mengganti asset stable tersebut.
