# Asset workflow

## Inventory first

Inspect the source and the project's actual import path. The bundled inventory script reads only the supplied file: a `.gltf` report can name buffers or textures without proving they exist. An image embedded in a GLB is counted but its resolution is not decoded. Run a glTF validator and a real loader for those separate checks.

Keep the original file under a distinct name. Record the candidate source and licensing provenance; optimization does not grant permission to redistribute a model, texture or animation.

## External tool discovery

Blender and glTF Transform must be separately installed. Check their versions without starting a conversion:

```text
blender --version
gltf-transform --version
gltf-transform --help
```

If a command is absent, use the existing project tooling or explain the missing dependency. A Skill installation does not install these programs. An `npx` or package-manager command may download and execute third-party code; it is not a read-only version probe unless an installed executable is used.

Use the installed CLI's help as the authority for flags. The following are small command examples, not a mandatory universal pipeline:

```text
gltf-transform inspect source.glb
gltf-transform validate source.glb
gltf-transform dedup source.glb candidate-dedup.glb
gltf-transform inspect candidate-dedup.glb
gltf-transform validate candidate-dedup.glb
```

Check command availability before executing. Do not add `--allow-net` for an asset with external URIs unless fetching those resources is intended and authorized. Consult the [official CLI reference](https://gltf-transform.dev/cli) for current command behavior; the `optimize` preset has several effects and is not automatically appropriate for rigged or gameplay-linked assets.

## Source editing and export

Use Blender only when changes require it, such as editing geometry, UVs, a pivot or rig. Reopening and exporting an otherwise valid asset can itself change data. Inspect the current scene, export selection and animation settings; do not overwrite the source `.blend` just to produce a runtime candidate.

Make units, forward direction and the attachment/collision naming convention explicit. Applying object transforms on a rig or animated object can change behavior; verify a representative clip before and after. Preserve the required skeleton and clip names. Export a separate GLB or a `.gltf` plus its complete local resource set according to the runtime's established contract.

## Choose the operation by the bottleneck

| Observed problem | Candidate operation | Evidence needed after |
|---|---|---|
| Repeated identical resources | Deduplication or intentional instancing | Rendering and gameplay lookups still match |
| Excess geometry for projected size | A separate simplified mesh or LOD | Silhouette, UV seams, normals and skin deformation |
| Heavy network geometry | Meshopt or Draco, when supported | Actual transfer/decode time and decoder availability |
| Texture transfer or GPU memory | Resolution adjustment or KTX2/Basis encoding | Fine detail, alpha, normal map quality, color treatment |
| Excess runtime submissions | Material reuse, batching or instancing | Measured draw calls without broken interaction boundaries |

Do not estimate GPU memory savings from compressed download size alone. Texture formats and decoding determine runtime storage. Keep color textures and data textures on their appropriate color-space path; normal/roughness/metalness data must not be “visually corrected” as ordinary color artwork.

LODs need an actual runtime selection strategy; exporting several files does not make the game use them. Collision proxies are separate gameplay assets and should remain simpler than the visible mesh where appropriate. Test the character against floors, slopes and narrow openings after changing scale or colliders.

## Compression integration

For Three.js, inspect the project's existing GLTFLoader setup before adding another loader instance. A candidate using Draco, Meshopt or KTX2 requires the corresponding supported decoder/transcoder path. Test those resources in the deployed base path as well as local development. Self-hosting decoders may suit an offline game; an arbitrary CDN is not an assumed permission or availability guarantee.

Check the relevant official loader documentation for the installed Three.js version:

- [GLTFLoader](https://threejs.org/docs/pages/GLTFLoader.html)
- [DRACOLoader](https://threejs.org/docs/pages/DRACOLoader.html)
- [KTX2Loader](https://threejs.org/docs/pages/KTX2Loader.html)

Use the existing Babylon.js, PlayCanvas or other engine import API when that is the chosen runtime. This skill does not require migrating to Three.js.
