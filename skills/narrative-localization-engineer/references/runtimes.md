# Narrative runtime boundaries

[ink](https://github.com/inkle/ink) and [inkjs](https://github.com/y-lohse/inkjs) are MIT, but compiler and runtime formats must agree. Reviewed releases were ink 1.2.1 and inkjs 2.4.0; do not assume that date order proves compatibility. Compile a representative story and test save/load using the versions actually installed.

[Yarn Spinner for Unity](https://github.com/YarnSpinnerTool/YarnSpinner-Unity/releases/tag/v3.2.8) is MIT and has text/voice localization workflows; reviewed package minimum Unity 2022.3. [Yarn Godot GDScript](https://github.com/YarnSpinnerTool/YarnSpinner-Godot-GDScript/blob/main/LICENSE.md) has a different YSPL license. No Yarn runtime is bundled here.

Minimal local string-table format for the included checker:

```json
{"schema_version":1,"default_locale":"en","locales":{"en":{"welcome":"Welcome, {name}"},"zh-CN":{"welcome":"欢迎，{name}"}}}
```

All locale tables must contain the same IDs and the same counts of plain `{name}` placeholders. Empty strings are errors; optional `warn_length` (positive integer, default 240) is only a layout-review hint. ICU plurals/select expressions need a matching project parser, not this checker. Read localization exports as data. Escape rendered content using the project's UI framework and allowlist game commands separately from text.
