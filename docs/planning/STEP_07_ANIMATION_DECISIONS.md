# STEP 07 — Animation / Transition / Spectrum Decisions

Status: **PASS**  
Phase: **PLANNING**  
Coding: **BLOCKED**

## Decisions
- **D07-01** AnimationEvaluator is pure/deterministic and shared by Preview/Render semantics.
- **D07-02** Use existing Layer.animation with versioned fam-animation v1; no project schema bump.
- **D07-03** Only registered typed property IDs are animatable.
- **D07-04** Evaluation order: base/legacy -> manual keyframe -> BeatResponse -> clamp.
- **D07-05** Animation variety comes from reusable tracks/responses/presets, not renderer branches.
- **D07-06** Visual transitions never silently alter audio crossfade/timing.
- **D07-07** BeatAnalysis derived data and BeatResponse authored behavior remain separate.
- **D07-08** Animation v1 allows at most one BeatResponse per target property.
- **D07-09** Reactive effects modulate bounded numeric properties; graph topology stays stable.
- **D07-10** Existing FFmpeg Spectrum remains canonical; expand via presets/transforms/response.
- **D07-11** Circular Spectrum is production-proven and remains bounded/parity-tested.
- **D07-12** Generic authored animation wins per-property; otherwise legacy motion remains.
- **D07-13** Fallback never fakes audio reactivity; resting/non-reactive state is allowed.
- **D07-14** Every new effect family requires Accurate Preview vs Final Render golden evidence.
- **D07-15** Animation complexity scales with layers/keyframes/events, not duration × FPS Python data.
- **D07-16** Preset registry is declarative, versioned, validated, and non-executable.
- **D07-17** Beat-reactive animations target visual properties only; master audio remains untouched.
- **D07-18** Initial implementation proves a small animation core before expanding preset catalog.

## Existing Production Spectrum That Must Be Preserved
- bars — FFmpeg showfreqs
- spectrum_line — FFmpeg showfreqs
- waveform — FFmpeg showwaves
- stereo_waveform — FFmpeg showwaves split channels
- circular_spectrum — showfreqs + bounded polar GEQ remap

## Compatibility
Existing image motion, visual transition, video speed, vinyl spin, effect seed/speed/intensity, and Spectrum properties remain load-compatible. New generic animation must not double-apply a property that is already owned by a legacy behavior.

## Known Cleanup
`overlay_effects.py` contains stale legacy metadata claiming circular Spectrum is unavailable. Production code/tests prove circular Spectrum is available. Remove/retire that stale capability flag only during implementation cleanup after tests protect current behavior.

## Next
STEP 08 — Feature Parity, Enhancement, dan AI Agent Reliability.
