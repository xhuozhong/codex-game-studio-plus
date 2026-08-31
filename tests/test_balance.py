"""Portable standard-library tests: python tests/test_balance.py."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True

BASE = Path(__file__).resolve().parents[1]
SCRIPT = BASE / 'skills/gameplay-balance-validator/scripts/validate_telemetry.py'
spec = importlib.util.spec_from_file_location('balance_checker', SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def run(policy='timed', seed=42, score=2):
    return {'run_id': policy + '-' + str(seed), 'policy': policy, 'policy_version': '1',
            'configuration_id': 'config-a', 'seed': seed, 'tick_rate': 60, 'max_ticks': 600,
            'elapsed_ticks': 120, 'status': 'completed', 'end_state': 'game_over',
            'initial_score': 0, 'score': score,
            'coverage': dict.fromkeys(['input', 'spawn', 'score', 'death'], 'recorded'),
            'events': [{'id': 'a', 'tick': 0, 'type': 'spawn', 'entity_id': 'target1'},
                       {'id': 'b', 'tick': 5, 'type': 'input', 'actor': 'p1', 'action': 'pulse', 'accepted': True},
                       {'id': 'c', 'tick': 5, 'type': 'score', 'delta': score, 'opportunity_id': 'target1-life1', 'reason': 'hit'},
                       {'id': 'd', 'tick': 120, 'type': 'death', 'cause': 'collision'}]}


def doc(*runs):
    return {'schema_version': 1, 'runs': list(runs)}


class BalanceTests(unittest.TestCase):
    def test_valid_pair_is_deterministic_and_accounts_events(self):
        data = doc(run('hold', 42, 1), run('timed', 42, 3))
        first = checker.validate_document(data, 'hold', 'timed')
        second = checker.validate_document(copy.deepcopy(data), 'hold', 'timed')
        self.assertEqual(first, second)
        self.assertFalse(first['telemetry_errors'])
        self.assertEqual(first['comparison']['paired_runs'][0]['score_difference'], 2)
        self.assertEqual(first['comparison']['paired_runs'][0]['score_ratio'], 3)
        self.assertEqual(first['runs'][0]['event_counts']['score'], 1)

    def test_zero_and_negative_denominators(self):
        for baseline_score in (0, -2):
            result = checker.validate_document(doc(run('hold', score=baseline_score), run()), 'hold', 'timed')
            self.assertIsNone(result['comparison']['paired_runs'][0]['score_ratio'])
            self.assertEqual(result['comparison']['paired_runs'][0]['score_difference'], 2 - baseline_score)
            json.dumps(result, allow_nan=False)

    def test_overflow_comparison_returns_an_error(self):
        result = checker.validate_document(doc(run('hold', score=10**308), run(score=-(10**308))), 'hold', 'timed')
        self.assertTrue(any('overflow' in error for error in result['telemetry_errors']))
        self.assertIsNone(result['comparison'])
        json.dumps(result, allow_nan=False)

    def test_repeated_opportunity_count_and_opt_in_cap(self):
        data = run(score=3)
        data['events'][2]['delta'] = 1
        data['events'].insert(3, {'id': 'e', 'tick': 6, 'type': 'score', 'delta': 1, 'opportunity_id': 'target1-life1', 'reason': 'hit'})
        data['events'].insert(4, {'id': 'f', 'tick': 7, 'type': 'score', 'delta': 1, 'opportunity_id': 'target1-life2', 'reason': 'hit'})
        observed = checker.validate_document(doc(data))
        self.assertFalse(observed['telemetry_errors'])
        self.assertFalse(observed['rule_violations'])
        self.assertEqual(observed['runs'][0]['repeated_score_events'], 1)
        self.assertEqual(observed['runs'][0]['unique_scoring_opportunities'], 2)
        enforced = checker.validate_document(doc(data), max_scores=1)
        self.assertEqual(len(enforced['rule_violations']), 1)

    def test_duplicate_event_is_invalid_telemetry(self):
        data = run()
        data['events'][2]['id'] = 'b'
        result = checker.validate_document(doc(data))
        self.assertTrue(any('duplicate event IDs' in error for error in result['telemetry_errors']))
        self.assertEqual(result['runs'][0]['duplicate_event_ids'], {'b': 2})

    def test_cooldown_boundaries_and_rejection(self):
        for tick, expected in [(9, 1), (10, 0)]:
            data = run()
            data['events'].insert(3, {'id': 'e', 'tick': 8, 'type': 'input', 'actor': 'p1', 'action': 'pulse', 'accepted': False})
            data['events'].insert(4, {'id': 'f', 'tick': tick, 'type': 'input', 'actor': 'p1', 'action': 'pulse', 'accepted': True})
            result = checker.validate_document(doc(data), cooldown=5)
            self.assertEqual(len(result['rule_violations']), expected)

    def test_bad_events_and_accounting_block_comparison(self):
        mutations = [lambda r: r['events'][2].pop('delta'),
                     lambda r: r['events'][0].update(tick=-1),
                     lambda r: r['events'][2].update(delta=float('nan')),
                     lambda r: r['events'][2].update(delta=10**1000),
                     lambda r: r.update(score=99),
                     lambda r: r['events'][1].update(accepted='yes'),
                     lambda r: r['coverage'].update(score='not_applicable')]
        for mutate in mutations:
            data = run()
            mutate(data)
            result = checker.validate_document(doc(run('hold'), data), 'hold', 'timed')
            self.assertTrue(result['telemetry_errors'])
            self.assertIsNone(result['comparison'])

    def test_harness_failure_is_not_zero_score(self):
        failed = {key: value for key, value in run().items() if key in ('run_id', 'policy', 'policy_version', 'configuration_id')}
        failed.update(status='harness_error', error='browser lost focus')
        result = checker.validate_document(doc(run('hold'), failed), 'hold', 'timed')
        self.assertFalse(result['telemetry_errors'])
        self.assertEqual(result['harness_error_count'], 1)
        self.assertEqual(result['comparison']['paired_runs'], [])
        self.assertIsNone(result['comparison']['median_score_difference'])

    def test_pairing_respects_seed_config_and_versions(self):
        candidate = run(seed='42')
        result = checker.validate_document(doc(run('hold'), candidate), 'hold', 'timed')
        self.assertEqual(len(result['comparison']['unmatched_runs']), 2)
        candidate['seed'] = 42
        candidate['configuration_id'] = 'config-b'
        result = checker.validate_document(doc(run('hold'), candidate), 'hold', 'timed')
        self.assertEqual(len(result['comparison']['unmatched_runs']), 2)
        candidate = run(seed=43)
        candidate['policy_version'] = '2'
        result = checker.validate_document(doc(run(), candidate))
        self.assertTrue(any('mixed policy_version' in e for e in result['telemetry_errors']))

    def test_duplicate_pairs_and_run_ids_invalid(self):
        for new_id in ('timed-42', 'unique'):
            repeated = run()
            repeated['run_id'] = new_id
            result = checker.validate_document(doc(run('hold'), run(), repeated), 'hold', 'timed')
            self.assertTrue(result['telemetry_errors'])
            self.assertIsNone(result['comparison'])

    def test_unseeded_runs_not_paired(self):
        result = checker.validate_document(doc(run('hold', None), run('timed', None)), 'hold', 'timed')
        self.assertEqual(result['comparison']['paired_runs'], [])
        self.assertEqual(len(result['comparison']['unseeded_runs_excluded']), 2)

    def test_cli_exit_codes_and_nonfinite_json(self):
        cases = [(doc(run()), [], 0), (doc(run()), ['--max-scores-per-opportunity', '0'], 2)]
        bad = run()
        bad['events'].insert(3, {'id': 'e', 'tick': 6, 'type': 'input', 'actor': 'p1', 'action': 'pulse', 'accepted': True})
        cases.append((doc(bad), ['--cooldown-ticks', '5'], 1))
        with tempfile.TemporaryDirectory(prefix='codex-balance-test-') as scratch:
            for i, (data, args, code) in enumerate(cases):
                fixture = Path(scratch) / ('balance-fixture-' + str(i) + '.json')
                fixture.write_text(json.dumps(data), encoding='utf-8')
                process = subprocess.run([sys.executable, str(SCRIPT), str(fixture)] + args, capture_output=True, text=True)
                self.assertEqual(process.returncode, code, process.stderr)
                json.loads(process.stdout)
            fixture.write_text('{"schema_version":1,"runs":NaN}', encoding='utf-8')
            process = subprocess.run([sys.executable, str(SCRIPT), str(fixture)], capture_output=True, text=True)
            self.assertEqual(process.returncode, 2)
            self.assertIn('non-finite', process.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
