# Loading and failure handling

Adapted from the official Phaser `loading-assets` skill at the pinned commit in [source provenance](../source-provenance.json). This version adds a failure gate rather than equating loader completion with successful asset delivery. Check the [version gate](version-and-config.md) first.

## Queue, complete, then verify

Queue assets in `preload()`: Phaser starts the loader for that phase. Loading methods called later only queue work; start the loader with `this.load.start()` and wait for the relevant completion before constructing objects. Register listeners before starting the load. Do not call `start()` repeatedly on every update or click.

The loader's `complete` event supplies `(loader, totalComplete, totalFailed)`. Completion means the queue has finished processing; it does not mean every asset succeeded. Use `loaderror` to record failed keys, and check required textures/data before starting gameplay. Show an actionable error or a deliberate fallback; avoid entering a scene with missing required resources.

```js
// 'PlayScene' must be registered by the project; hero.png is a project asset.
class BootScene extends Phaser.Scene {
    constructor() {
        super('BootScene');
    }

    init() {
        this.failedKeys = [];
    }

    preload() {
        this.onAssetError = (file) => this.failedKeys.push(file.key);
        this.load.on('loaderror', this.onAssetError);
        this.events.once(Phaser.Scenes.Events.SHUTDOWN, () => {
            this.load.off('loaderror', this.onAssetError);
        });
        this.load.image('hero', 'assets/hero.png');
    }

    create() {
        this.load.off('loaderror', this.onAssetError);
        if (this.failedKeys.length || !this.textures.exists('hero')) {
            this.add.text(24, 24, 'Required assets failed to load. Check the asset path and retry.');
            return;
        }
        this.scene.start('PlayScene');
    }
}
```

In a real retry UI, disable duplicate retry clicks, clear the recorded failure state for the new attempt, and requeue only the intended files. Preserve any existing retry/backoff policy instead of adding an unbounded retry loop. For a lazy load, verify that the requesting scene is still entitled to consume the result if it can shut down while loading.

## Match asset format and ownership

| Asset | Loader choice | Integration condition |
| --- | --- | --- |
| One image | `this.load.image(key, url)` | Construct the image after successful loading |
| Regular grid of animation frames | `this.load.spritesheet(key, url, { frameWidth, frameHeight })` | Use the actual frame dimensions, margin and spacing |
| Packed named frames | `this.load.atlas(key, textureURL, atlasURL)` | Texture and metadata must correspond; frame names are case-sensitive |
| Tiled map | `this.load.tilemapTiledJSON(key, url)` plus the tileset image | Map key, Tiled tileset name and texture key are different identifiers |
| JSON | `this.load.json(key, url)` | Check the expected structure before using it as gameplay configuration |

Textures and typed caches are game-wide. Namespacing keys avoids collisions across levels. Loading a second image with a key already in the texture manager does not replace it automatically. Before removing or replacing a shared texture, identify all active consumers and make the lifetime transition deliberately.

`setPath('assets/')` affects URLs; `setPrefix('LEVEL1.')` affects cache keys. A prefixed image named `hero` must be used as `LEVEL1.hero`. Debug the resolved network URL and the cache key separately. Test via the project's HTTP development server, especially when reproducing CORS or deployment-path failures. Do not bypass browser security to hide a failed cross-origin request.

## Focused acceptance check

Load the happy path, intentionally use a missing required asset in an isolated test, and verify that the failure is visible and gameplay does not proceed with a broken resource. Restore the asset before delivery. Inspect network failures and console errors, not just the loading bar. If changing a deployment base path, test the built game under that path, including map/atlas companion files. If changing a lazy load, navigate away mid-load and reopen it to check for stale callbacks or duplicate listeners.

Pinned source: [loading assets](https://github.com/phaserjs/phaser/blob/02d8931b626d9764c133cbb3fbf99966c03c757c/skills/loading-assets/SKILL.md). MIT notice: [LICENSE.txt](../LICENSE.txt).
