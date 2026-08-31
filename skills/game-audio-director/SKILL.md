---
name: game-audio-director
description: "Implement and validate game music, sound effects and voice playback, including cue mapping, mixing, looping, spatial audio and pause/resume. Use for audio systems and asset integration, not general visual feedback."
---

# Game audio director

Define an audio event table tied to real game actions. Record BGM/SFX/voice groups, priorities, concurrency limits, loop boundaries, ducking and pause/background behavior. Reuse the engine's audio system; for browser projects evaluate Howler for playback or Tone only when musical scheduling/synthesis is needed.

## Prepare assets

Keep source WAV and shipping encodes separately. Record source/voice permissions and codec alternatives. A library's MIT license does not authorize songs, samples, actors' voices or model outputs. Audio generation requires an available authorized service; this skill does not bundle one.

The included Python 3.10+ [WAV checker](scripts/audio_audit.py) measures integer PCM sample peak/RMS, silence, full-scale sample count and optional loop frame bounds. It supports 8/16/24/32-bit PCM, not arbitrary compressed audio or LUFS.

```text
python <skill-dir>/scripts/audio_audit.py --input source.wav
python <skill-dir>/scripts/audio_audit.py --input loop.wav --loop-start 0 --loop-end 48000
```

Full-scale samples are a warning to inspect, not proof that all audio is clipped. Numerically valid loop points do not prove an inaudible seam. Never report listening based only on a waveform, screenshot or metadata.

## Runtime acceptance

Unlock browser audio through a genuine user interaction and handle unavailable devices/decoders. Separate musical clock scheduling from rendering frames. Ensure one gameplay event yields one intended cue; cap overlapping effects and release audio on scene exit. Preserve user volume/mute settings and provide captions or other alternatives for essential voice information.

Listen in context: first interaction, rapid repeated action, pause/resume, tab background/foreground, missing asset, scene restart and voice over music. Record which browser/device and what was actually heard. If audio monitoring is unavailable, state that playback state was checked but listening remains pending.

Version and provider references: [audio tools](references/tools.md).
