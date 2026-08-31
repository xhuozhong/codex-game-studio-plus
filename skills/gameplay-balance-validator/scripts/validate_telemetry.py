#!/usr/bin/env python3
"""Validate exported game telemetry; never runs or judges a game. Python 3.9+."""
import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import sys


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def number(value):
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def integer(value, minimum=0):
    return type(value) is int and value >= minimum


def validate_run(run, max_scores=None, cooldown=None):
    errors, violations = [], []
    if not isinstance(run, dict):
        return None, ['run must be an object'], violations
    for key in ('run_id', 'policy', 'policy_version', 'configuration_id'):
        if not nonempty(run.get(key)):
            errors.append(key + ' must be a nonempty string')
    if errors:
        return None, errors, violations
    summary = {key: run[key] for key in ('run_id', 'policy', 'policy_version', 'configuration_id')}
    summary['status'] = run.get('status')
    if run.get('status') == 'harness_error':
        if not nonempty(run.get('error')):
            errors.append('harness_error requires an error description')
        return summary, errors, violations
    if run.get('status') != 'completed':
        errors.append('status must be completed or harness_error')
    if not (run.get('seed') is None or type(run.get('seed')) is int or nonempty(run.get('seed'))):
        errors.append('seed must be an integer, nonempty string, or null')
    if 'seed' not in run:
        errors.append('seed is required; use null when unavailable')
    if not number(run.get('tick_rate')) or run['tick_rate'] <= 0:
        errors.append('tick_rate must be a positive finite number')
    for key in ('max_ticks', 'elapsed_ticks'):
        if not integer(run.get(key)):
            errors.append(key + ' must be a nonnegative integer')
    if not errors and run['elapsed_ticks'] > run['max_ticks']:
        errors.append('elapsed_ticks exceeds max_ticks')
    for key in ('initial_score', 'score'):
        if not number(run.get(key)):
            errors.append(key + ' must be a finite number')
    if not nonempty(run.get('end_state')):
        errors.append('end_state must be a nonempty string')
    coverage = run.get('coverage', {})
    categories = ('input', 'spawn', 'score', 'death')
    if not isinstance(coverage, dict) or any(coverage.get(k) not in ('recorded', 'not_applicable') for k in categories):
        errors.append('coverage must declare all four event categories')
    if not isinstance(run.get('events'), list):
        errors.append('events must be an array')
    if errors:
        return summary, errors, violations

    ids, opportunities, event_counts = Counter(), Counter(), Counter()
    accepted_at = {}
    score_deltas = []
    previous_tick = -1
    for index, event in enumerate(run['events']):
        label = 'event ' + str(index)
        if not isinstance(event, dict):
            errors.append(label + ': must be an object')
            continue
        if not nonempty(event.get('id')) or not integer(event.get('tick')):
            errors.append(label + ': id and nonnegative integer tick are required')
            continue
        ids[event['id']] += 1
        tick, kind = event['tick'], event.get('type')
        if tick < previous_tick or tick > run['elapsed_ticks']:
            errors.append(label + ': tick is out of order or beyond elapsed_ticks')
        previous_tick = tick
        if kind not in categories:
            errors.append(label + ': unsupported event type')
            continue
        event_counts[kind] += 1
        if coverage[kind] != 'recorded':
            errors.append(label + ': event contradicts coverage declaration')
        if kind == 'score':
            if not number(event.get('delta')) or not nonempty(event.get('opportunity_id')) or not nonempty(event.get('reason')):
                errors.append(label + ': score requires finite delta, opportunity_id, and reason')
                continue
            score_deltas.append(event['delta'])
            # A repeat is observational unless an explicit scoring cap was requested.
            opportunities[event['opportunity_id']] += 1
        elif kind == 'input':
            if not nonempty(event.get('actor')) or not nonempty(event.get('action')) or type(event.get('accepted')) is not bool:
                errors.append(label + ': input requires actor, action, and boolean accepted')
                continue
            if event['accepted']:
                key = (event['actor'], event['action'])
                if cooldown is not None and key in accepted_at and tick - accepted_at[key] < cooldown:
                    violations.append(label + ': accepted input inside cooldown for ' + repr(key))
                accepted_at[key] = tick
        elif kind == 'spawn' and not nonempty(event.get('entity_id')):
            errors.append(label + ': spawn requires entity_id')
        elif kind == 'death' and not nonempty(event.get('cause')):
            errors.append(label + ': death requires cause')

    duplicate_ids = {key: count for key, count in sorted(ids.items()) if count > 1}
    if duplicate_ids:
        errors.append('duplicate event IDs: ' + ', '.join(duplicate_ids))
    try:
        accounted_score = math.fsum([run['initial_score']] + score_deltas)
    except (OverflowError, ValueError):
        accounted_score = None
        errors.append('score event sum is not finite')
    if accounted_score is not None and not math.isclose(accounted_score, run['score'], rel_tol=1e-9, abs_tol=1e-9):
        errors.append('initial_score + event deltas does not match final score')
    if max_scores is not None:
        for key, count in sorted(opportunities.items()):
            if count > max_scores:
                violations.append('opportunity ' + repr(key) + ' scored ' + str(count) + ' times; cap ' + str(max_scores))
    summary.update({key: run[key] for key in ('seed', 'tick_rate', 'max_ticks', 'elapsed_ticks', 'score', 'end_state')})
    summary.update(event_counts=dict(sorted(event_counts.items())), duplicate_event_ids=duplicate_ids,
                   unique_scoring_opportunities=len(opportunities),
                   repeated_score_events=sum(count - 1 for count in opportunities.values()),
                   repeated_opportunities={key: count for key, count in sorted(opportunities.items()) if count > 1})
    return summary, errors, violations


def validate_document(document, baseline=None, candidate=None, max_scores=None, cooldown=None):
    report = {'telemetry_errors': [], 'rule_violations': [], 'runs': [], 'comparison': None}
    if not isinstance(document, dict) or type(document.get('schema_version')) is not int or document['schema_version'] != 1 or not isinstance(document.get('runs'), list) or not document['runs']:
        report['telemetry_errors'].append('expected schema_version 1 and a nonempty runs array')
        return report
    if (max_scores is not None and not integer(max_scores, 1)) or (cooldown is not None and not integer(cooldown)):
        report['telemetry_errors'].append('invalid scoring cap or cooldown')
        return report
    if bool(baseline) != bool(candidate) or (baseline is not None and baseline == candidate):
        report['telemetry_errors'].append('comparison requires two different policies')
        return report
    seen_ids, versions = set(), defaultdict(set)
    valid = []
    for index, run in enumerate(document['runs']):
        summary, errors, violations = validate_run(run, max_scores, cooldown)
        label = str(run.get('run_id', index)) if isinstance(run, dict) else str(index)
        if summary:
            if summary['run_id'] in seen_ids:
                errors.append('duplicate run_id')
            seen_ids.add(summary['run_id'])
            versions[summary['policy']].add(summary['policy_version'])
            report['runs'].append(summary)
            if not errors and summary['status'] == 'completed':
                valid.append(summary)
        report['telemetry_errors'].extend(label + ': ' + e for e in errors)
        report['rule_violations'].extend(label + ': ' + e for e in violations)
    for policy, values in sorted(versions.items()):
        if len(values) > 1:
            report['telemetry_errors'].append(policy + ': mixed policy_version values; use separate reports')
    report['runs'].sort(key=lambda item: item['run_id'])
    report['harness_error_count'] = sum(r['status'] == 'harness_error' for r in report['runs'])
    if baseline and not report['telemetry_errors']:
        by_key = defaultdict(dict)
        for run in valid:
            if run['policy'] not in (baseline, candidate) or run['seed'] is None:
                continue
            key = (run['configuration_id'], type(run['seed']).__name__, str(run['seed']), run['tick_rate'], run['max_ticks'])
            if run['policy'] in by_key[key]:
                report['telemetry_errors'].append('multiple runs for the same policy/configuration/seed; split replicates into reports')
            by_key[key][run['policy']] = run
        pairs, unmatched = [], []
        for key, policies in sorted(by_key.items()):
            if baseline not in policies or candidate not in policies:
                unmatched.extend(r['run_id'] for r in policies.values())
                continue
            left, right = policies[baseline], policies[candidate]
            difference = right['score'] - left['score']
            ratio = right['score'] / left['score'] if left['score'] > 0 else None
            if not number(difference) or (ratio is not None and not number(ratio)):
                report['telemetry_errors'].append('comparison overflow; rescale score units')
                continue
            pairs.append({'baseline_run': left['run_id'], 'candidate_run': right['run_id'],
                          'score_difference': difference, 'score_ratio': ratio,
                          'ratio_note': 'descriptive only' if ratio is not None else 'undefined for nonpositive baseline'})
        if not report['telemetry_errors']:
            differences = sorted(p['score_difference'] for p in pairs)
            middle = len(differences) // 2
            median = (differences[middle] if len(differences) % 2 else differences[middle - 1] / 2 + differences[middle] / 2) if differences else None
            report['comparison'] = {'baseline': baseline, 'candidate': candidate, 'paired_runs': pairs,
                                    'unmatched_runs': sorted(unmatched),
                                    'unseeded_runs_excluded': sorted(r['run_id'] for r in valid if r['seed'] is None and r['policy'] in (baseline, candidate)),
                                    'median_score_difference': median,
                                    'interpretation': 'Descriptive paired results only; no significance or fun verdict.'}
    return report


def reject_constant(value):
    raise ValueError('non-finite JSON constant: ' + value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--baseline')
    parser.add_argument('--candidate')
    parser.add_argument('--max-scores-per-opportunity', type=int)
    parser.add_argument('--cooldown-ticks', type=int)
    args = parser.parse_args()
    try:
        document = json.loads(args.input.read_text(encoding='utf-8-sig'), parse_constant=reject_constant)
        result = validate_document(document, args.baseline, args.candidate, args.max_scores_per_opportunity, args.cooldown_ticks)
    except (OSError, ValueError, UnicodeError) as exc:
        result = {'telemetry_errors': [str(exc)], 'rule_violations': [], 'runs': [], 'comparison': None}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False))
    return 2 if result['telemetry_errors'] else 1 if result['rule_violations'] else 0


if __name__ == '__main__':
    sys.exit(main())
