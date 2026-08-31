"""Check a JSON string table for missing text, duplicates and placeholder drift."""
import argparse
import json
import re
import sys
from pathlib import Path
from collections import Counter

def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result

def audit(data):
    errors, warnings = [], []
    if not isinstance(data, dict) or data.get('schema_version') != 1:
        raise ValueError('Expected schema_version=1')
    locales, default = data.get('locales'), data.get('default_locale')
    if not isinstance(locales, dict) or default not in locales or not isinstance(locales[default], dict) or not locales[default]:
        raise ValueError('Expected nonempty default locale and locale dictionaries')
    base = locales[default]
    for language, strings in locales.items():
        if not isinstance(strings, dict):
            errors.append(language + ': expected text dictionary')
            continue
        for key in set(base) - set(strings):
            errors.append(f'{language}: missing text id {key}')
        for key in set(strings) - set(base):
            errors.append(f'{language}: unknown text id {key}')
        for key, value in strings.items():
            if not isinstance(value, str) or not value.strip():
                errors.append(f'{language}/{key}: empty or non-string text')
                continue
            original = base.get(key)
            if isinstance(original, str):
                pattern = r'\{([A-Za-z_][A-Za-z0-9_]*)\}'
                if Counter(re.findall(pattern, value)) != Counter(re.findall(pattern, original)):
                    errors.append(f'{language}/{key}: placeholder names/counts differ')
            if len(value) > data.get('warn_length', 240):
                warnings.append(f'{language}/{key}: inspect long text in actual UI')
    return {'ok': not errors, 'locales': sorted(locales), 'text_ids': len(base), 'errors': sorted(errors),
            'warnings': sorted(warnings), 'limitation': 'Plain {name} placeholders only; no ICU parsing, translation quality, voice or layout verification.'}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', required=True)
    a = p.parse_args()
    try:
        data = json.loads(Path(a.input).read_text(encoding='utf-8-sig'), object_pairs_hook=unique_object)
        if type(data.get('warn_length', 240)) is not int or data.get('warn_length', 240) < 1:
            raise ValueError('warn_length must be a positive integer')
        result = audit(data)
    except (ValueError, OSError, TypeError, AttributeError) as exc:
        result = {'ok': False, 'errors': [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['ok'] else 1

if __name__ == '__main__':
    sys.exit(main())
