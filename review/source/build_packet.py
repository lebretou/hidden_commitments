from pathlib import Path
import json, hashlib, shutil
ROOT=Path(__file__).resolve().parents[2]
data=json.loads((ROOT/'dataset_draft.json').read_text())
# Whitelist review content. Exclude labels, rationales, sampling notes, and summaries.
blind=[{**{k:e[k] for k in ['id','domain','split','transcript','transcript_sha256']},'source_uid':e.get('source_uid','Synthetic conversation'),'questions':[{k:q[k] for k in ['id','text','options']} for q in e['questions']]} for e in data]
blind.sort(key=lambda e:(e['split']!='pilot',e['domain']!='meetingbank',e['id']))
fingerprint=hashlib.sha256(json.dumps(blind,sort_keys=True).encode()).hexdigest()
template=(ROOT/'review/source/template.html').read_text()
payload=json.dumps({'version':fingerprint,'examples':blind},ensure_ascii=False).replace('<','\\u003c')
(ROOT/'review/review.html').write_text(template.replace('__PAYLOAD__',payload))
shutil.copy2(ROOT/'review_key_draft.txt',ROOT/'review/draft-key-open-after-review.txt')
print('Created blind form:',len(blind),'conversations;',sum(len(e['questions']) for e in blind),'questions')
