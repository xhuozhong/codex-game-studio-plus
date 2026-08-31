---
name: phaser-specialist
description: Implement and debug Phaser browser games with version-aware scene, asset-loading, Arcade Physics, and tilemap guidance. Use for an existing Phaser project or when the user has chosen Phaser, not to replace another engine.
---

# Phaser Specialist

Own Phaser-specific implementation details while preserving the project's chosen engine, major version, physics system, and build tooling. This is a selective adaptation of the official Phaser skills, not an engine distribution or an automatic migration tool.

## Establish the version before choosing an API

Read the dependency declaration and lockfile, then the installed package metadata or bundled runtime when available. Record the resolved Phaser version; a range in `package.json` alone is not the installed version. For a CDN build, inspect its pinned URL and the loaded `Phaser.VERSION` through the project's permitted inspection tools. If these disagree, resolve the mismatch before changing engine-specific code.

The bundled upstream snapshot is Phaser **4.2.1**. Read [version and configuration](references/version-and-config.md) before relying on these references in a Phaser 3 project. Keep Phaser 3 projects on their existing major version unless migration is requested; verify APIs against that installed version's types/source and version-matched official documentation. Do not install or upgrade Phaser merely because these references use version 4.

## Load only the relevant reference

| Task | Reference |
| --- | --- |
| Renderer/configuration choices, Phaser 3 versus 4 differences | [Version and configuration](references/version-and-config.md) |
| Restarting, switching, overlays, duplicate callbacks or stale state | [Scenes and lifecycle ownership](references/scenes-and-lifecycle.md) |
| Preload, missing assets, cache keys or lazy loading | [Loading and failure handling](references/loading-and-errors.md) |
| Arcade bodies, triggers, Tiled layers, collision or coordinates | [Arcade Physics and tilemaps](references/physics-and-tilemaps.md) |

For Matter Physics, shaders, audio, animation, or plugins not covered here, inspect the installed API and fetch only the needed official version-matched material. Do not assume Arcade body methods apply to Matter bodies or that a Phaser 4 rendering feature exists in Phaser 3.

## Delivery and verification

Implement the requested playable slice in the existing scene structure. Register persistent colliders/listeners at their owning lifecycle boundary, reset restartable state in `init`, and clean external subscriptions on shutdown. Keep resource ownership explicit across parallel scenes and shared caches.

Use the project's existing build/type checks and available browser-testing workflow. Exercise the changed behavior, restart the relevant scene repeatedly, check input and collision once per intended action, and inspect browser errors and failed asset requests. Test pause/resume or mobile layout when the change touches them. Report the actual Phaser version, files changed, checks performed, and any untested behavior; a successful build does not prove playable behavior.

The team director remains the task coordinator. Hand off broader balance, artwork preparation, or game-feel decisions when relevant rather than duplicating those experts' work.

## Source and license

References are edited selections from `phaserjs/phaser`, pinned to commit `02d8931b626d9764c133cbb3fbf99966c03c757c`, with additional integration safeguards. The original MIT copyright and license are retained verbatim in [LICENSE.txt](LICENSE.txt). File-level source hashes and modifications are listed in [source-provenance.json](source-provenance.json). These examples were statically reviewed during packaging; they are not a claim of runtime compatibility testing.
