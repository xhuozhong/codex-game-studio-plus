# Renderer-specific VFX

[pmndrs/postprocessing v6.39.4](https://github.com/pmndrs/postprocessing/releases/tag/v6.39.4) is a Three WebGL route, with Zlib license and reviewed Three dependency `>=0.168.0 <0.186.0`. It is not a drop-in WebGPU renderer or Phaser/Unity effect stack. Check the actual lockfile and backend before adding it. No third-party shader code is bundled here.

For Phaser use its installed version's supported pipeline, blend modes and particle APIs. For Unity/Godot use the project's render pipeline and editor, not Three postprocessing examples. Review shader compilation, color-space conversions and render target formats in that engine.

Suggested evidence: fixed camera/resolution comparison, actual frame-time measurements, shader/console error log, event count for repeated triggers, and resource counts before/after scene reload. User-facing flash/motion settings should alter the effect without hiding necessary gameplay feedback. Screenshots cannot establish frame time or prove resource cleanup.
