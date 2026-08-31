# Runtime acceptance

Choose a representative camera route and device/browser set before comparing. Match camera, lights, resolution, quality settings and test state for baseline and candidate.

- Load using the game's shipping asset path; inspect missing decoder, buffer and texture requests.
- Confirm required extensions are supported. A JSON inventory alone cannot establish decoder compatibility.
- Check material appearance, transparent/cutout edges, double-sided surfaces, normal maps and roughness under the game's lighting.
- Play each required animation, including transitions; inspect skinning, root movement and named attachments.
- Check interaction pivots, world scale and collider placement. Run collision checks if collision-related data changed.
- Exercise repeated loading/unloading if this asset is streamed; check retained objects and GPU-resource disposal using the project's renderer tools.
- Compare network bytes, load/decode duration, representative frame time and memory with the same measurement method. Label estimates and unavailable measurements.
- Test the deployed base path and caching configuration. A local success does not prove the decoder URL is correct after deployment.

## Report template

```text
Asset / intended use:
Source file and SHA-256:
Candidate file and SHA-256:
Tool versions and exact transformations:
Required runtime extensions / decoder assets:
Baseline -> candidate transfer bytes:
Baseline -> candidate load/decode time, device and method:
Baseline -> candidate frame time / memory, if measured:
Visual and gameplay checks performed:
Animation clips checked:
Known differences and rollback path:
Not tested / remaining dependency:
```

Store before/after evidence near the project artifact without publishing private source paths, credentials or unrelated game assets. Update the asset index only after the acceptance checks appropriate to the user's task pass.
