# Scenes and lifecycle ownership

Adapted from the official Phaser `scenes` and `events-system` skills at the pinned commit in [source provenance](../source-provenance.json). Examples add explicit ownership/cleanup and omit the upstream full API catalog. Check the [version gate](version-and-config.md) first.

## Choose the intended scene transition

| Operation through `this.scene` | Intended behavior |
| --- | --- |
| `start('LevelTwo', data)` | Shut down the current scene and start the target |
| `restart(data)` | Shut down and start this scene again |
| `launch('UIScene', data)` | Start another scene without stopping this one |
| `run('UIScene', data)` | Start, resume or wake the target according to its state |
| `pause()` / `resume()` | Stop/restart updating while keeping the scene rendered |
| `sleep()` / `wake()` | Suspend/restore updating and rendering while preserving state |
| `stop()` | Shut down a scene that may later restart |
| `remove(key)` | Permanently remove/destroy the scene |

Scene start/stop requests may be queued by the scene manager. Do not assume the target's `create()` has finished on the next line after requesting a transition. Use a scene lifecycle event or an explicit ready signal when another component must wait for it. Guard repeated input so that holding a button does not enqueue repeated transitions.

`init(data)` runs each start/restart; constructors do not. Reset run-specific score, death flags, arrays and pending-action state in `init`, while keeping long-lived configuration separate. `preload` queues assets; `create` builds the scene once loading finishes; `update(time, delta)` runs while active. A failed asset request can still reach `create`: see [loading and failure handling](loading-and-errors.md).

## Local versus global ownership

Scene display objects, input, timers and physics plugins belong to their scene. Texture/cache managers, the registry and game event emitter are shared. An overlay that listens to the registry or another scene must unsubscribe from that emitter when it shuts down; hiding or sleeping it does not automatically silence subscriptions.

Use the same function reference and context when removing a listener. Remove only listeners this component owns. Calling `removeAllListeners()` on a shared emitter can disable unrelated systems.

```js
// Register ScoreUI alongside the gameplay scene; launch it when needed.
class ScoreUI extends Phaser.Scene {
    constructor() {
        super('ScoreUI');
    }

    create() {
        this.scoreText = this.add.text(16, 16, '');
        this.onScoreChanged(null, this.registry.get('score') ?? 0);
        this.registry.events.on('changedata-score', this.onScoreChanged, this);
        this.registry.events.on('setdata', this.onDataCreated, this);

        this.events.once(Phaser.Scenes.Events.SHUTDOWN, () => {
            this.registry.events.off('changedata-score', this.onScoreChanged, this);
            this.registry.events.off('setdata', this.onDataCreated, this);
        });
    }

    onScoreChanged(parent, value) {
        this.scoreText.setText('Score: ' + value);
    }

    onDataCreated(parent, key, value) {
        if (key === 'score') this.onScoreChanged(parent, value);
    }
}
```

The gameplay owner writes `this.registry.set('score', value)`. Keep one authoritative score value; the UI displays it rather than independently adding points from duplicate subscriptions. A new key emits `setdata`; an existing key emits `changedata-score`, so the sample handles both and cleans up both subscriptions. If an overlay should ignore changes while sleeping, implement that policy explicitly and resynchronize it when waking.

For browser/DOM listeners, sockets, custom intervals or subscriptions outside Phaser's scene-owned systems, keep the cleanup callback alongside registration and dispose at the relevant shutdown boundary. For a custom resource that survives shutdown by design, dispose it at final destruction instead. Do not assume scene shutdown closes an external connection.

## Focused acceptance check

Restart the affected scene several times and perform one action after each restart. It should still produce one score update, one sound, one request or one transition as intended. Compare relevant shared-emitter listener counts before/after where observable. Exercise pause/resume and overlay reopen if those paths were changed; check that paused gameplay cannot accept an unintended action through an external callback. Verify state reset separately from resource cleanup.

Pinned sources: [scenes](https://github.com/phaserjs/phaser/blob/02d8931b626d9764c133cbb3fbf99966c03c757c/skills/scenes/SKILL.md), [events](https://github.com/phaserjs/phaser/blob/02d8931b626d9764c133cbb3fbf99966c03c757c/skills/events-system/SKILL.md), [registry event semantics](https://github.com/phaserjs/phaser/blob/02d8931b626d9764c133cbb3fbf99966c03c757c/src/data/DataManager.js). MIT notice: [LICENSE.txt](../LICENSE.txt).
