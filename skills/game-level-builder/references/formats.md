# Map formats and boundaries

- [Tiled](https://github.com/mapeditor/tiled), reviewed v1.12.2: editor/plugins GPL, libtiled BSD; exported map data and third-party art have separate rights. The checker accepts finite numeric JSON, including flip flag masking, and external TSJ/JSON tilesets. It rejects TSX and base64/compressed/chunked layer data rather than guessing. Optional spawn checks assume a point origin, map-sized unshifted grid and nonzero solid cells; arbitrary object collision requires the game's physics.
- [LDtk](https://github.com/deepnight/ldtk), reviewed v1.5.3 with current mainline docs: editor MIT; sample art has separate licenses. The checker reads project `levels`, `worlds`, optional `.ldtkl` files, tileset paths, IntGrid lengths and entity IID uniqueness. It does not interpret EntityRef fields or generated engine scripts. Validate those using the project's importer.

For either route, keep stable IDs in saves and gameplay bindings; do not depend on array order or display names alone. Re-exporting should not duplicate entities or break trigger targets. A map containing all its image files can still have incorrect pivots, masks, navigation or runtime behavior.
