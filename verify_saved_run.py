"""Replay the completed experiment from cached calls without a GPU or network."""
import json
from pathlib import Path
import shutil
import tempfile

from pilot import Runner, digest, score

ROOT = Path(__file__).resolve().parent


def verify():
    inputs = json.loads((ROOT / 'experiment_inputs.json').read_text())
    labels = json.loads((ROOT / 'dataset_draft.json').read_text())
    saved = {}
    for path in (ROOT / 'results').glob('*.json'):
        item = json.loads(path.read_text())
        if isinstance(item, dict) and item.get('configuration', {}).get('runner_version') == '0.2.0' and 'example_id' in item:
            if item['example_id'] in saved:
                raise ValueError('Duplicate saved example: ' + item['example_id'])
            saved[item['example_id']] = item
    if set(saved) != {e['id'] for e in inputs}:
        raise ValueError('Saved examples do not match the input dataset')
    config = next(iter(saved.values()))['configuration']
    if any(item['configuration'] != config for item in saved.values()):
        raise ValueError('Saved examples contain different configurations')
    used = set()
    for item in saved.values():
        used.update(c['call_key'] for c in item['conditions'])
        used.add(item['generated_summary_call'])
        used.update(item['tracker']['call_keys'])
    for key in used:
        record = json.loads((ROOT / 'results/calls' / (key + '.json')).read_text())
        expected = digest({'messages': record['messages'], 'max_tokens': record['max_new_tokens'], 'config': config})
        if key != expected or record['key'] != key:
            raise ValueError('Cache key mismatch: ' + key)

    def no_inference(messages, max_tokens):
        raise RuntimeError('Cache miss: verification must not call a model')

    with tempfile.TemporaryDirectory(prefix='commitment-replay-') as tmp:
        shutil.copytree(ROOT / 'results/calls', Path(tmp) / 'calls')
        runner = Runner(no_inference, config, tmp)
        replay = [runner.run_example(ex) for ex in inputs]
        for item in replay:
            if item != saved[item['example_id']]:
                raise ValueError('Replayed result differs: ' + item['example_id'])
        replay_scores = score(replay, labels)
        analysis = json.loads((ROOT / 'analysis.json').read_text())
        if replay_scores['summary'] != analysis['summary']:
            raise ValueError('Replayed scores differ from analysis.json')
    print(f'Verified {len(saved)} examples and {len(used)} call keys. Cached replay and scores match; no inference performed.')


if __name__ == '__main__':
    verify()
