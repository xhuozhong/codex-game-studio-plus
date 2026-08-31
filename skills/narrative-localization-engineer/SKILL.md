---
name: narrative-localization-engineer
description: "Integrate branching dialogue, narrative state, localization tables, subtitles and voice mappings into games. Use for story-runtime and translation integration, not unrestricted prose writing."
---

# Narrative and localization engineer

Separate authored story from gameplay commands and persistent state. Establish stable text/line IDs, explicit command bindings, variable ownership and save migration policy. Do not execute arbitrary code from imported story files or translated strings.

## Select the existing runtime

For browsers, ink with inkjs is an option, but compiler/story format/runtime versions must agree. For Unity, ink or Yarn can suit the project. Yarn Unity's license does not apply to every Yarn product. Read [runtime notes](references/runtimes.md) when selecting a new backend. Neither this skill nor a story runtime supplies translations, recorded voices or licensed fonts.

## Keep text and voice in sync

Use locale-independent IDs for UI text, dialogue and optional voice. Define fallback text/voice behavior, subtitle timing and missing-translation reporting. Localized line breaks, CJK glyph coverage and variable-length names require real layout checks. Render untrusted translated text safely; avoid interpreting it as HTML or game commands.

The Python 3.10+ [table checker](scripts/localization_audit.py) checks duplicate JSON keys, missing/extra IDs, empty text and plain `{name}` placeholder multiplicity. Input has `schema_version: 1`, `default_locale` and `locales` mapping locale names to ID/string dictionaries. It is not an ICU or ink/Yarn parser.

```text
python <skill-dir>/scripts/localization_audit.py --input locales.json
```

## Runtime acceptance

Traverse each meaningful branch/condition of the changed story, including loops and invalid choices. Save and restore before/after a choice, switch language mid-dialogue, test missing voice/translation and long strings, and validate command arguments. Confirm restored state does not duplicate rewards or re-run one-shot events. Test old saves explicitly when changing compiled content or IDs.

Deliver authored story, compiled version mapping, text/voice manifest, localization diagnostics and actual game evidence. Syntax and ID checks are not evidence of translation quality, complete branch coverage or legal voice rights.
