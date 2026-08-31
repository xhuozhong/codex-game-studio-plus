# Manifest v1

All file paths are relative to the supplied project root, use `/` separators, and must identify regular local files. Absolute paths, traversal, alternate data streams, symlinks and junctions are rejected. Source descriptions/URLs are metadata, never fetched. The CLI outputs JSON to stdout; use the caller's normal artifact-writing mechanism if a saved report is needed.

Top-level fields: `schema_version` (1), `assets` (array).

Each asset has `id` (lowercase letters/digits with dot, dash or underscore), `kind` (image, texture, model, animation, audio, map, font, ui, data), `path`, `sha256`, nonempty `source`, `license` with `id`, and `status` (draft, processed, verified). Optional `depends_on` contains asset IDs, `max_bytes` a positive project-specific budget, and `evidence` local paths to reports/screenshots. Use `UNKNOWN` for unresolved licensing instead of inventing a grant.

For `--release`, every asset additionally needs `license.reviewed: true`, `license.evidence` pointing to the local authorization/license record, `status: verified`, and nonempty `evidence`. Those fields are declarations to be reviewed by the person/agent doing the work; the checker cannot determine whether a license actually grants the intended rights or a screenshot demonstrates correctness. It checks declared dependency existence, not dependency graph acyclicity.

Example record shape (replace paths with the project's actual files and obtain the hash with `record`):

```json
{"id":"hero","kind":"model","path":"assets/hero.glb","sha256":"computed-by-record","source":"self-authored by project team","license":{"id":"UNKNOWN","reviewed":false},"status":"draft","depends_on":[],"evidence":[]}
```

Retain original/derived file lineage and generation metadata as additional fields: author, original URL, download date, workflow path, model/node versions and hashes, seed, reference inputs, asset channel/axis/animation contracts. These extra fields are not interpreted by the checker. Keep secrets out of manifests and workflow exports.
