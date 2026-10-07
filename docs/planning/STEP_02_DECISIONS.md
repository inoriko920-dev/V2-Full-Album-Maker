# STEP 02 — Riset Pondasi Matang, Lisensi, dan Keputusan Adopsi

Status: **PASS**

This file is a compact handoff. The detailed STEP 02 DOCX remains the authoritative planning artifact.

## Official Decisions

| ID | Decision |
|---|---|
| D02-01 | FFmpeg/ffprobe remain the final render/probe engine. |
| D02-02 | PySide6 remains the UI toolkit; no toolkit rewrite. |
| D02-03 | MLT is reference-only. |
| D02-04 | libopenshot is reference-only; study reader/cache/lifecycle/beat-sync patterns. |
| D02-05 | PyAV is deferred until Python 3.12 has an independent architectural reason. |
| D02-06 | imageio-ffmpeg is reference-only; avoid a second FFmpeg distribution. |
| D02-07 | MoviePy is reference-only and not a renderer foundation. |
| D02-08 | projectM is only an optional isolated post-V2 visualizer/plugin candidate. |
| D02-09 | NumPy 2.3.x is the primary future BeatAnalysis runtime candidate. |
| D02-10 | SciPy is deferred unless tests/benchmarks prove it is needed. |
| D02-11 | librosa is a research/test oracle, not a portable dependency. |
| D02-12 | aubio and Essentia are rejected for core/distribution. |
| D02-13 | Python >=3.11 remains the initial stabilization baseline. |
| D02-14 | Third-party license/compliance evidence becomes a release quality gate. |
| D02-15 | Current V2 repo remains the foundation; external technology enters only through adapters, benchmarks, and rollback-capable integration. |

## Beat Analysis Direction

Target concept for later architecture planning:

```text
Audio source
  -> bundled FFmpeg decode to mono PCM
  -> BeatAnalysisService
      -> RMS/energy envelope
      -> low/mid/high band energy
      -> spectral flux/onset envelope
      -> peaks/beat timestamps/confidence
      -> optional tempo estimate
  -> fingerprinted AnalysisCache
  -> BeatResponse curves
  -> PreviewEngine + RenderEngine
```

Potential response profiles include Beat Pulse, Bass Pump, Mid Motion, Treble Spark, Onset Burst, Tempo Phase, Energy Smooth, and Silence Gate.

Hard rules:
- deterministic analysis/cache;
- preview and render consume the same analysis;
- beat effects never change audio timing;
- non-reactive fallback remains available;
- user can disable beat-reactive behavior.

## License/Packaging Direction
- Application code remains MIT.
- Bundled FFmpeg is a separate third-party binary and must carry its applicable license/compliance evidence.
- PySide6/Qt compliance must remain explicit in release planning.
- Do not copy GPL/AGPL source into the MIT codebase.
- New native dependencies require Windows portable clean-machine testing.
- Do not bundle duplicate FFmpeg stacks without an explicit approved decision.

## Next
STEP 03 — Target Architecture V2 dan Strategi Migrasi Bertahap.
