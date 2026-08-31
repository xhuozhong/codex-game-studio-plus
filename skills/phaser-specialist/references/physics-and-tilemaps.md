# Arcade Physics and tilemaps

Adapted from the official Phaser `physics-arcade` and `tilemaps` skills at the pinned commit in [source provenance](../source-provenance.json). This selection joins map loading and collision setup, adds failure guards and omits version-specific performance claims that need measurement. Check the [version gate](version-and-config.md) first.

## Bodies, collisions and triggers

Use this reference only for Arcade Physics. Preserve a project's Matter Physics implementation and use its own body/collision APIs when Matter is configured.

Arcade velocity is in pixels per second. Do not multiply `setVelocityX` values by frame delta; the physics world integrates motion. Position changes outside physics need their own timing/ownership decision. Inspect body bounds separately from sprite art when collisions look wrong.

Create a persistent `this.physics.add.collider(a, b)` or `this.physics.add.overlap(a, b, callback, processCallback, context)` once at the owning scene's setup boundary. Creating them in `update()` adds repeated collision processors. `collider` separates bodies; `overlap` detects without separation and is suitable for pickups. When an owned collider becomes obsolete before scene shutdown, destroy that collider rather than altering the world's unrelated registrations.

Disable a consumed pickup's body before awarding score to prevent repeated processing. A compact callback adapted from upstream is:

```js
// Used as an Arcade overlap callback with the scene passed as context.
function collectCoin(player, coin) {
    if (!coin.body || !coin.body.enable) return;
    coin.disableBody(true, true);
    this.registry.set('score', (this.registry.get('score') ?? 0) + 10);
}
```

Static bodies do not automatically follow later changes to a game object's position, origin or scale. For an Arcade static sprite/image, call `refreshBody()` after those changes. Use a dynamic/kinematic approach supported by the chosen engine for moving platforms; do not assume that visually tweening a static platform creates correct riding behavior.

## Tiled JSON to collidable layer

Read the map's exported names and tileset settings before coding. The Tiled tileset name, Phaser texture key and Tiled layer name are distinct, case-sensitive values. Use embedded tileset data and a tileset image format supported by the installed Phaser parser; the pinned parser does not support Tiled's collection-of-images tilesets.

```js
// Example for an already configured Phaser 4 Arcade scene.
// The project supplies the three asset files and registers this scene.
class MapScene extends Phaser.Scene {
    constructor() {
        super('MapScene');
    }

    preload() {
        this.load.tilemapTiledJSON('level', 'assets/level.json');
        this.load.image('terrainTexture', 'assets/terrain.png');
        this.load.image('player', 'assets/player.png');
    }

    create() {
        // Use the failure-handling pattern from loading-and-errors.md first.
        if (!this.cache.tilemap.exists('level') ||
            !this.textures.exists('terrainTexture') ||
            !this.textures.exists('player')) {
            this.add.text(24, 24, 'Map assets are missing.');
            return;
        }

        const map = this.add.tilemap('level');
        const tileset = map.addTilesetImage('Terrain', 'terrainTexture');
        if (!tileset) throw new Error('Missing Tiled tileset: Terrain');
        const ground = map.createLayer('Ground', tileset);
        if (!ground) throw new Error('Missing or already-created layer: Ground');

        // Requires a boolean collides property on solid tiles in Tiled.
        ground.setCollisionByProperty({ collides: true });
        this.player = this.physics.add.sprite(100, 100, 'player');
        this.physics.world.setBounds(0, 0, map.widthInPixels, map.heightInPixels);
        this.player.setCollideWorldBounds(true);
        this.physics.add.collider(this.player, ground);
    }
}
```

Adapt the names and spawn position to the real map; the example does not bundle assets or controls. Check that the spawn is outside solid tiles. Map rendering alone does not enable collision: set the desired tile collision properties/indexes and add the physics collider. Grouped Tiled layer names may use `Parent/Child`. Avoid creating the same map layer twice.

Tile coordinates are not world pixels. Use layer coordinate-conversion/query APIs instead of manually dividing world coordinates when layer offsets, scale or map orientation matter. A tile query may return `null`; check before reading `properties`. Keep hazards/triggers semantically distinct from solid ground and verify overlap behavior for the installed engine rather than assuming the solid-tile filter applies identically to triggers.

## Phaser 4 GPU layer boundary

The pinned Phaser 4 API accepts a fifth `gpu` argument to `map.createLayer`. This option is not a default optimization for every map: upstream documents WebGL-only, orthogonal maps, and one tileset per GPU layer. Runtime tile edits require `generateLayerDataTexture()` to update what is displayed. Retain ordinary layers for unsupported orientations/multiple tilesets or when profiling does not justify a change. Never paste this option into a Phaser 3 project without checking actual API support.

## Focused acceptance check

Enable physics debug visuals only for development inspection, then disable them in release configuration. Check body/art alignment, boundaries, corner contacts, one pickup awarding once, restart resetting the world, and a changed tile's render/collision behavior. For movement changes compare behavior at different render rates. Record actual frame time/body counts before changing spatial-index or physics-step settings; do not import arbitrary object-count thresholds as guarantees.

Pinned sources: [Arcade Physics](https://github.com/phaserjs/phaser/blob/02d8931b626d9764c133cbb3fbf99966c03c757c/skills/physics-arcade/SKILL.md), [tilemaps](https://github.com/phaserjs/phaser/blob/02d8931b626d9764c133cbb3fbf99966c03c757c/skills/tilemaps/SKILL.md). MIT notice: [LICENSE.txt](../LICENSE.txt).
