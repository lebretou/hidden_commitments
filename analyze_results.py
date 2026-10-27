"""Recompute pilot metrics from saved v0.2.0 examples; no GPU needed."""
import json
from collections import defaultdict
from pathlib import Path
from pilot import score
ROOT=Path(__file__).resolve().parent

def analyze():
    labels=json.loads((ROOT/'dataset_draft.json').read_text())
    examples={e['id']:e for e in labels}
    results=[]
    for p in sorted((ROOT/'results').glob('*.json')):
        r=json.loads(p.read_text())
        if isinstance(r,dict) and r.get('configuration',{}).get('runner_version')=='0.2.0' and 'example_id' in r:
            results.append(r)
    ids=[r['example_id'] for r in results]
    if len(ids)!=len(set(ids)): raise ValueError('Multiple configurations for one example; select a single run explicitly.')
    metrics=score(results,labels)
    costs=defaultdict(lambda:dict(calls=0,input_tokens=0,output_tokens=0,seconds=0,output_limit_hits=0))
    failures=[];errors=[];used=set();max_gpu=0
    for r in results:
        ex=examples[r['example_id']]
        keygroups={c['method']:[c['call_key']] for c in r['conditions']}
        keygroups['summary_preprocessing']=[r['generated_summary_call']]
        keygroups['tracker_preprocessing']=r['tracker']['call_keys']
        for method,keys in keygroups.items():
            for key in keys:
                call=json.loads((ROOT/'results'/'calls'/(key+'.json')).read_text())
                used.add(key);max_gpu=max(max_gpu,call.get('peak_gpu_gib',0))
                c=costs[(r['domain'],r['split'],method)]
                c['calls']+=1;c['input_tokens']+=call.get('input_tokens',0)
                c['output_tokens']+=call.get('output_tokens',0)
                c['seconds']+=call.get('generation_seconds',call['elapsed_seconds'])
                c['output_limit_hits']+=int(call.get('hit_output_limit',False))
        failures.append({'id':r['example_id'],'rejected_attempts':len(r['tracker']['rejected_updates']),
            'failed_chunks':sum(h['failed'] for h in r['tracker']['history']),
            'chunks':len(r['tracker']['history']),'final_records':len(r['tracker']['memory']['current_records'])})
    for row in metrics['questions']:
        if row['correct']: continue
        ex=examples[row['example_id']];q=next(q for q in ex['questions'] if q['id']==row['question_id'])
        errors.append({**row,'question':q['text'],'expected_text':q['answer_text'],
            'predicted_text':q['options'].get(row['predicted']),'draft_evidence':q['evidence_quote'],'rationale':q['rationale']})
    metrics['costs']=[dict(domain=k[0],split=k[1],method=k[2],**v) for k,v in sorted(costs.items())]
    metrics['tracker_checks']=failures;metrics['errors']=errors
    metrics['coverage']={'completed_ids':ids,'expected':len(labels),'missing_ids':sorted(set(examples)-set(ids)),
                         'unique_inference_calls':len(used),'peak_gpu_gib':max_gpu}
    (ROOT/'analysis.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2))
    print(json.dumps({'coverage':metrics['coverage'],'summary':metrics['summary'],'tracker_checks':failures},indent=2))
    return metrics

if __name__=='__main__': analyze()
