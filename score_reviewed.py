"""Rescore a completed run with team-adjudicated answer choices.
Usage: python score_reviewed.py adjudicated_review.json
Input uses independent_review_template.json's format. This records supplied reviewer
claims; software cannot certify that review was human or independent.
Original draft labels and scores are preserved.
"""
import json,sys
from pathlib import Path
from pilot import score
ROOT=Path(__file__).resolve().parent

def rescore(path):
    labels=json.loads((ROOT/'dataset_draft.json').read_text())
    expected={(e['id'],q['id']) for e in labels for q in e['questions']}
    review=json.loads(Path(path).read_text());lookup={}
    for row in review:
        key=(row['example_id'],row['question_id'])
        if key not in expected or key in lookup: raise ValueError('Unknown or duplicate question: '+str(key))
        if row.get('answer') not in list('ABCD') or not row.get('reviewer','').strip():
            raise ValueError('Each adjudicated item needs a reviewer and A-D answer: '+str(key))
        lookup[key]=row
    if set(lookup)!=expected: raise ValueError('Complete all 66 items or explicitly create a separate subset evaluation.')
    changed=[]
    for ex in labels:
        for q in ex['questions']:
            row=lookup[(ex['id'],q['id'])]
            if row['answer']!=q['answer']: changed.append(q['id'])
            q['answer']=row['answer'];q['answer_text']=q['options'][row['answer']]
            q['review_record']=row
        ex['annotation_status']='team_supplied_adjudication; verify review procedure separately'
    results=[]
    for p in sorted((ROOT/'results').glob('*.json')):
        r=json.loads(p.read_text())
        if isinstance(r,dict) and r.get('configuration',{}).get('runner_version')=='0.2.0' and 'example_id' in r: results.append(r)
    if len({r['example_id'] for r in results})!=len(results): raise ValueError('Duplicate result configurations')
    scores=score(results,labels)
    scores['label_status']='Scored against supplied adjudication; human-review process must be verified separately'
    scores['changed_keys']=changed
    (ROOT/'dataset_adjudicated.json').write_text(json.dumps(labels,ensure_ascii=False,indent=2))
    (ROOT/'scores_adjudicated.json').write_text(json.dumps(scores,ensure_ascii=False,indent=2))
    print(json.dumps({'changed_keys':changed,'summary':scores['summary']},indent=2))

if __name__=='__main__': rescore(sys.argv[1])
