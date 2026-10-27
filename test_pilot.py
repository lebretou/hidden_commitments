import copy
import json
import tempfile
import unittest
from pathlib import Path
from pilot import Runner, chunk_text, conversation_chunks, score, validate_delta

ROOT=Path(__file__).parent

class PilotTests(unittest.TestCase):
    def test_chunks_preserve_every_character(self):
        text=('A sentence.\nAnother sentence with Friday conditions. '*100)
        chunks=chunk_text(text,75)
        self.assertEqual(''.join(c['text'] for c in chunks),text)
        self.assertTrue(all(c['text']==text[c['start']:c['end']] for c in chunks))

    def test_unsupported_and_stale_evidence_rejected(self):
        r={'id':'c1','owner':'A','action':'send','conditions':None,'deadline':None,'status':'active','uncertainty':None,'evidence':['I will send it.']}
        self.assertEqual(validate_delta({'upserts':[r]},'I will send it.','I will send it.',{}),[])
        self.assertTrue(validate_delta({'upserts':[r]},'I will send it. Later.','Later.',{}))
        r['evidence']=['fabricated quote']
        self.assertTrue(validate_delta({'upserts':[r]},'I will send it.','I will send it.',{}))

    def test_inputs_do_not_leak_labels_and_groups_are_disjoint(self):
        xs=json.loads((ROOT/'experiment_inputs.json').read_text())
        ys=json.loads((ROOT/'dataset_draft.json').read_text())
        self.assertEqual(len(xs),22)
        self.assertEqual(sum(len(x['questions']) for x in xs),66)
        for x in xs:
            for q in x['questions']:
                self.assertEqual(set(q),{'id','kind','text','options'})
        for y in ys:
            for q in y['questions']:
                self.assertIn(q['evidence_quote'],y['transcript'])
                self.assertEqual(q['options'][q['answer']],q['answer_text'])
        self.assertFalse({x['meeting_group'] for x in xs if x['split']=='dev'} & {x['meeting_group'] for x in xs if x['split']=='pilot'})

    def test_cache_is_bound_to_prompt_and_configuration(self):
        calls=[]
        def fake(messages,n): calls.append(messages);return 'ok'
        with tempfile.TemporaryDirectory() as t:
            r=Runner(fake,{'model':'first'},t)
            r.call('a',10,'x');r.call('a',10,'x');r.call('b',10,'x')
            Runner(fake,{'model':'second'},t).call('a',10,'x')
        self.assertEqual(len(calls),3)

    def test_missing_answers_count_as_failures(self):
        label={'id':'x','questions':[{'id':'q','answer':'B','kind':'owner'}]}
        result={'example_id':'x','domain':'synthetic','split':'pilot','conditions':[{'method':'tracker','answers':[],'errors':['invalid'],'source':''}]}
        out=score([result],[label])
        self.assertEqual(out['summary'][0]['n'],1)
        self.assertEqual(out['summary'][0]['correct'],0)
        self.assertEqual(out['summary'][0]['parse_failure_questions'],1)

    def test_cancellation_preserves_history_and_processes_each_turn(self):
        ex={'id':'test','domain':'synthetic','transcript':'A: I will send it.\nA: I cancel that promise.'}
        self.assertEqual(len(conversation_chunks(ex)),2)
        records=[{'id':'c1','owner':'A','action':'send it','conditions':None,'deadline':None,
                  'status':'active','uncertainty':None,'evidence':['I will send it.']},
                 {'id':'c1','owner':'A','action':'send it','conditions':None,'deadline':None,
                  'status':'cancelled','uncertainty':None,'evidence':['I cancel that promise.']}]
        def fake(messages,n):return json.dumps({'upserts':[records.pop(0)]})
        with tempfile.TemporaryDirectory() as t: out=Runner(fake,{'model':'test'},t).track(ex)
        self.assertEqual(out['memory']['current_records'][0]['status'],'cancelled')
        self.assertEqual(out['memory']['revisions'][0]['before']['status'],'active')
        self.assertEqual(out['memory']['revisions'][0]['after']['status'],'cancelled')

if __name__=='__main__': unittest.main()
