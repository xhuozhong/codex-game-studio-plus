# Browser audio tool routes

[Howler 2.2.4](https://github.com/goldfire/howler.js/blob/v2.2.4/README.md) provides playback, audio sprites, fades and spatial audio; MIT. Its release is older (2023), so test current target browsers rather than relying on a compatibility claim. Handle unlock/load/play errors and teardown in the project's lifecycle.

[Tone 15.1.22](https://github.com/Tonejs/Tone.js/blob/15.1.22/README.md) is useful for synthesis and musical clock scheduling; MIT. Its GitHub Release and development/npm versions can differ. Start audio following a real user gesture and schedule against the audio clock, not a rendering frame's arrival time. Do not load both libraries just because both are listed.

Keep a cue table: id, source asset, bus, trigger, loop range, concurrency/priority, gain, pause policy and subtitle/voice mapping. The included WAV tool reports sample peak/RMS, not perceived loudness or codec support. Listen for clicks at loop seams, duplicated cues, masked speech and long silence. Audio generator/model/service rights and performer consent are separate from playback-library licenses.
