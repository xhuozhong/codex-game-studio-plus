# Version and configuration

Adapted from the official Phaser `game-setup-and-config` and `v3-to-v4-migration` skills at the commit in [source provenance](../source-provenance.json). This reference intentionally omits the upstream upgrade checklist: adopting this specialist is not permission to upgrade the game. The source snapshot's `package.json` declares **4.2.1**.

## Establish what actually runs

Check the dependency and lockfile first. Confirm the installed `phaser/package.json`, or the actual script URL/runtime version for a CDN build. A project may declare a range, serve a different cached bundle, or use a custom build. Use that resolved version's types and source for signatures and availability; resolve discrepancies before modifying the code.

For Phaser 3, retain its current APIs and fetch documentation for that exact supported version. Treat the examples below as a Phaser 4 snapshot, even when an API happens to be shared. For an unknown major version, do not infer compatibility from a similar name.

## Configuration decisions that affect implementation

- Reuse the existing `Phaser.Game` instance and entrypoint. Adding a second instance to fix a scene issue can duplicate canvases, input and game loops.
- `Phaser.AUTO` chooses WebGL when possible and otherwise Canvas. `Phaser.WEBGL` has no Canvas fallback. A fallback is useful only if the chosen features support it; Phaser 4 filters and GPU tile layers must not be promised on Canvas.
- `Phaser.HEADLESS` skips rendering but still needs a DOM environment. It is not proof that the browser bundle can run in plain Node.js.
- Use `Phaser.Scale.FIT` when preserving a fixed gameplay coordinate space; use `RESIZE` only when the scene handles changes to its playable bounds and layout. Preserve the project's choice unless the task requires a change.
- Match texture filtering to artwork. `pixelArt: true` also changes anti-aliasing and pixel-rounding configuration; it is not simply a CSS setting. Test fractional scaling before claiming pixel-perfect output.
- Enable the physics plugin explicitly in the existing game or scene configuration before using `this.physics` or `this.matter`. Do not replace the chosen physics engine to make a copied example work.

For an already chosen Phaser 4/Arcade project, a configuration shape is:

```js
// GameScene must be defined/imported by the project's entrypoint.
const config = {
    type: Phaser.AUTO,
    parent: 'game-container',
    width: 800,
    height: 600,
    scale: {
        mode: Phaser.Scale.FIT,
        autoCenter: Phaser.Scale.CENTER_BOTH
    },
    physics: {
        default: 'arcade',
        arcade: { gravity: { x: 0, y: 300 }, debug: false }
    },
    scene: GameScene
};
```

This is a configuration excerpt, not a bundled runnable game. The page must supply the parent element and the project must create the game in its existing entrypoint.

## Version boundaries worth checking

These are differences described by the pinned upstream migration guide, not instructions to apply them to an unrelated task:

| Area | Phaser 3 code to recognize | Phaser 4 boundary |
| --- | --- | --- |
| Custom rendering | WebGL pipelines | Render-node architecture; custom pipelines need explicit migration work |
| Effects and masks | `preFX` / `postFX`, `BitmapMask` | Unified filters; do not paste filter APIs into Phaser 3 |
| Fill tint | `setTintFill()` | `setTint()` plus tint mode |
| Dynamic textures | Earlier immediate drawing assumptions | Buffered work needs `render()` |
| Tilemaps | Existing layer APIs and plugins | GPU layers are a separate version-4 capability with constraints |
| Camera internals | Matrix/scroll assumptions | Matrices changed; prefer stable camera properties where sufficient |

If migration is explicitly requested, first inventory the actual affected APIs, plugins and renderer requirements. Scope the migration separately and compare playable behavior before and after. Do not treat a dependency bump as a complete migration.

Pinned sources: [configuration](https://github.com/phaserjs/phaser/blob/02d8931b626d9764c133cbb3fbf99966c03c757c/skills/game-setup-and-config/SKILL.md), [migration](https://github.com/phaserjs/phaser/blob/02d8931b626d9764c133cbb3fbf99966c03c757c/skills/v3-to-v4-migration/SKILL.md), [package version](https://github.com/phaserjs/phaser/blob/02d8931b626d9764c133cbb3fbf99966c03c757c/package.json). MIT notice: [LICENSE.txt](../LICENSE.txt).
