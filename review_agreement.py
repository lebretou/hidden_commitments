"""Usage: python review_agreement.py reviewer1.json reviewer2.json
Reports pre-adjudication agreement for independently completed shared items.
This cannot establish that the review was independent; that is a team procedure.
"""
import json,sys

def compare(a,b):
    def checked(rows):
        out={}
        for row in rows:
            key=(row['example_id'],row['question_id'])
            if key in out: raise ValueError('Duplicate question in review file')
            if row.get('answer') in 'ABCD' and len(row.get('answer',''))==1:
                if not row.get('reviewer','').strip(): raise ValueError('Reviewer name is required for completed answers')
                out[key]=row
        return out
    aa,bb=checked(a),checked(b);shared=sorted(aa.keys() & bb.keys())
    if not shared: raise ValueError('No jointly completed questions')
    if any(aa[k]['reviewer']==bb[k]['reviewer'] for k in shared): raise ValueError('Two distinct human reviewers are required')
    n=len(shared);po=sum(aa[k]['answer']==bb[k]['answer'] for k in shared)/n
    return {'shared_questions':n,'shared_conversations':len({k[0] for k in shared}),
            'raw_agreement':po,'cohens_kappa':None,
            'disagreements':[{'example_id':k[0],'question_id':k[1],'reviewer1':aa[k],'reviewer2':bb[k]} for k in shared if aa[k]['answer']!=bb[k]['answer']],
            'caution':'Kappa is not computed for per-question shuffled options. For category-level kappa, independently annotate shared semantic categories on aligned records.'}

if __name__=='__main__':
    print(json.dumps(compare(*(json.load(open(p)) for p in sys.argv[1:3])),indent=2))
