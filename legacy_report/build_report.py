"""Build the editable-source midterm PDF from verified saved results.
Requires reportlab. Run analyze_results.py first and complete report_interpretation.json.
"""
import json
import re, html
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
ROOT=Path(__file__).resolve().parent
A=json.loads((ROOT.parent/'analysis.json').read_text())
I=json.loads((ROOT/'report_interpretation.json').read_text())
S=getSampleStyleSheet()
S.add(ParagraphStyle(name='Body',fontName='Times-Roman',fontSize=10,leading=12.4,spaceAfter=4.5,allowWidows=0,allowOrphans=0))
S.add(ParagraphStyle(name='Section',keepWithNext=True,fontName='Helvetica-Bold',fontSize=11,leading=14,spaceBefore=10,spaceAfter=5,textColor=colors.HexColor('#18394c')))
S.add(ParagraphStyle(name='SmallBody',fontName='Times-Roman',fontSize=9,leading=11.5,spaceAfter=4))
S.add(ParagraphStyle(name='Title2',fontName='Helvetica-Bold',fontSize=19,leading=23,spaceAfter=7))
S.add(ParagraphStyle(name='Subtitle',fontName='Helvetica',fontSize=9.5,leading=13,spaceAfter=9))
flow=[];text=[]
def p(s,style='Body'):
    flow.append(Paragraph(s,S[style]));text.append(s)
def h(s):p(s,'Section')
def table(rows,widths):
    data=[[Paragraph(escape(str(c)),S['SmallBody']) for c in row] for row in rows]
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#edf2f5')),('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#47616e')),('LINEBELOW',(0,-1),(-1,-1),.4,colors.HexColor('#a8b5bb')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
    flow.append(t);flow.append(Spacer(1,7));text.extend(' | '.join(map(str,r)) for r in rows)

p('Commitments Hidden in Conversation','Title2')
p('CMSC848N / Project 07 / Midterm progress report / 26 October 2026<br/>Klaudiusz Rydzy, Atharvan Dogra, Zhongzheng Xu<br/><b>Draft for team review. Annotation keys are AI-assisted and have not been independently human-validated.</b>','Subtitle')
h('1. Problem and midterm scope')
p('The project asks whether an agent can maintain an accurate, auditable record of who agreed to do what, under which conditions, and whether that agreement remains active. A statement such as "I will run the experiment if the dataset arrives by Friday" does not create an unconditional obligation when delivery later moves to Monday. Suggestions, intentions, accepted commitments, revisions, and completion reports must remain distinct.')
p('Our hypothesis is that explicit records of owners, conditions, status changes, and supporting utterances retain commitment-relevant information better than an ordinary meeting summary. This is a hypothesis to test, not an established limitation of every summary system. The midterm deliverable is a small runnable comparison, an annotation guide, draft data with traceable evidence, and an updated evaluation plan. Forecasting, fine-tuning, multilingual experiments, and final held-out-domain evaluation are deferred.')
h('2. Data and operational definitions')
p('MeetingBank provides public municipal meeting transcripts and reference summaries, but no ready-made commitment labels [1]. We sampled 30 validation entries with seed 848, inspected their contents, and purposively selected 12 manageable segments with relevant positive or negative cases. We also authored 10 short synthetic conversations with controlled condition failures, deadline changes, reassignment, cancellation, and completion evidence. The resulting 22 conversations have three multiple-choice probes each (66 questions).')
table([['Split','MeetingBank','Synthetic','Questions'],['Development','4 segments','2 conversations','18'],['Provisional pilot','8 segments','8 conversations','48']], [135,125,125,83])
p('The real and synthetic domains are scored separately. Source meetings do not cross development and pilot splits. This is a purposive pilot, not a representative benchmark or a held-out-domain test. Synthetic examples are checked for internal consistency and exact quoted evidence by the assistant; independent human checking is pending. Original noisy MeetingBank text is preserved without invented diarization. MeetingBank-derived data retains its CC-BY-NC-SA-4.0 attribution and reuse restrictions.')
p('The guide distinguishes suggestions, tentative intentions, firm and conditional commitments, uncertain interpretations, and reported institutional responsibilities. Permission to act and a request to act do not show personal acceptance. Satisfying a prerequisite does not establish task completion. Approximate dates remain approximate; a lease duration is not an execution deadline. Evidence quotations and draft rationales are supplied for every probe, but the probes are not exhaustive record annotations.')
h('3. System and comparison design')
p('We use the same Qwen3.8-27B checkpoint [4] for representation construction and answering. The model runs on a Colab A100-SXM4-40GB with NF4 4-bit double quantization, BF16 computation, batch size one, greedy decoding, and thinking disabled. The exact checkpoint revision, package versions, prompts, responses, timing, and token counts are retained. Model input plus requested output is capped at 16,384 tokens with an explicit error instead of silent truncation.')
p('Each example is evaluated using the complete selected transcript, its supplied reference summary (MeetingBank only), a newly generated ordinary prose summary, and an incremental structured tracker. A question-only control receives no conversation. Summaries and ledger updates are generated without seeing the questions or draft answer keys; the same three questions are then asked of each representation. Reference summaries are not fabricated for synthetic data.')
p('A tracker record contains a stable ID, owner, action, conditions, deadline, status, uncertainty, and exact evidence quotations. Real transcripts are processed in contiguous chunks of roughly 2,200 characters; synthetic conversations are processed one speaker turn at a time. Updates revise existing records and preserve previous versions. The validator checks the schema and that quoted evidence appears in the observed conversation, including evidence from the newest chunk. One repair is allowed; a still-invalid update leaves the previous state intact and records a failed chunk. Exact quotation matching checks provenance, not entailment.')
p('Generation limits are 512 tokens for a summary, 1,536 per tracker update, and 640 for each three-question answer. Thus the representations differ in length and preprocessing compute. The comparison is not compute-matched, and the transcript condition is a full-information baseline rather than a theoretical upper bound. Cached calls make interrupted runs resumable. Six local unit tests cover evidence checks, data separation, cache binding, scoring failures, and turn-by-turn state revision.')
h('4. Preliminary evidence')
p(I['coverage'])
p('Table 1 reports exact option accuracy against the current <b>draft</b> keys on the provisional pilot split. Development examples are excluded. Missing or malformed answers count as incorrect. These scores measure the QA probes, not commitment extraction precision/recall, semantic evidence validity, or the rate of unsupported records.')
lookup={(r['domain'],r['split'],r['method']):r for r in A['summary']}
rows=[['Representation','MeetingBank pilot','Synthetic pilot']]
for method,label in [('question_only','Question-only control'),('transcript','Full transcript'),('reference_summary','Reference summary'),('generated_summary','Generated summary'),('tracker','Structured tracker')]:
    cells=[label]
    for domain in ['meetingbank','synthetic']:
        r=lookup.get((domain,'pilot',method))
        cells.append(f"{r['correct']}/{r['n']} ({100*r['accuracy']:.1f}%)" if r else 'Not available')
    rows.append(cells)
table(rows,[192,138,138])
for s in I['findings']:p(s)
p(I['runtime'])
h('5. Interpretation and limitations')
p('The current question design contains many absent-commitment and absent-completion cases, some with conspicuously implausible alternatives. A strong question-only score can therefore expose shortcut answers; it prevents interpreting a high absolute score as evidence that a representation faithfully tracked dialogue. Three questions from the same conversation are correlated, and a few errors can substantially change these small-sample percentages. No statistical superiority claim is made.')
p('All keys and synthetic conversations were drafted with AI assistance. No two-human agreement has been measured, and no final human-adjudicated gold set exists yet. The implementation and guide share design choices with the question authoring, which may favor the tracker. Results are specific to one quantized model and decoding configuration; no full-precision or model-size ablation has been run. Other limitations include purposive selection, missing context at meeting segment boundaries, noisy speaker attribution, uneven representation budgets, and possible omission of unqueried commitments. A valid quotation can still be attached to a wrong owner or incorrect interpretation. We have not yet measured those semantic failures comprehensively.')
h('6. Related work')
p('Hu et al. [1] provide a municipal meeting summarization benchmark, not commitment labels or evidence that summaries systematically erase conditions. Heck et al. [2] motivate a zero-shot language-model dialogue-state baseline on a different task. Rezazadeh et al. [3] address shared agent memory, provenance, and access control, without commitment annotations. These works motivate our comparison; they do not predetermine which representation will retain commitments best.')
h('7. Updated plan')
p('<b>Before the midterm submission:</b> two team members independently answer the blind probes, report raw pre-adjudication agreement and sample size, resolve disagreements, and rescore the saved outputs. Inspect ambiguous ownership, conditions, and evidence attachments. Shuffled A-D options are not shared semantic categories for Cohen\'s kappa; a later category-level analysis needs aligned records and independently assigned speech-act labels.')
p('<b>Next phase:</b> expand toward 30 real segments with a documented sampling rule; annotate complete records at intermediate prefixes; and add minimal counterfactual pairs that differ only in acceptance, a date, or completion evidence. Use plausible distractors and balanced positive/negative probes. Measure owner/condition accuracy, correct revisions, unsupported-record frequency, and semantic evidence support. Lock the protocol before testing a different public dialogue domain. Defer forecasting until records are reliable.')
p('<b>AI assistance and contributions:</b> Codex assisted with this draft, code, synthetic data, draft labels, and analysis. The team must verify the claims, complete independent label review, and add actual individual contributions before submission. No human review or contribution is claimed on their behalf. The accompanying package contains runnable code, raw outputs, review forms, an annotation guide, and environment metadata.')
h('References')
refs=[
'[1] Hu et al. (2023). MeetingBank: A Benchmark Dataset for Meeting Summarization. https://arxiv.org/abs/2305.17529',
'[2] Heck et al. (2023). ChatGPT for Zero-shot Dialogue State Tracking: A Solution or an Opportunity? https://arxiv.org/abs/2306.01386',
'[3] Rezazadeh et al. (2025). Collaborative Memory: Multi-User Memory Sharing in LLM Agents with Dynamic Access Control. https://arxiv.org/abs/2505.18279',
'[4] Qwen. Qwen3.8-27B model card. https://huggingface.co/Qwen/Qwen3.8-27B. Revision: 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0.',
'[5] CMSC848N Fall 2026 course project rubric. https://furong-huang.com/cmsc848n-fall-2026/#project-rubrics. Accessed 26 October 2026.'
]
for r in refs:p(escape(r),'SmallBody')

def footer(canvas,doc):
    canvas.saveState();canvas.setStrokeColor(colors.HexColor('#c7d2d8'));canvas.line(54,43,558,43)
    canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#556570'))
    canvas.drawString(54,30,'CMSC848N | Midterm draft | Human label review pending')
    canvas.drawRightString(558,30,str(doc.page));canvas.restoreState()

doc=SimpleDocTemplate(str(ROOT/'midterm_report_draft.pdf'),pagesize=(612,792),rightMargin=66,leftMargin=66,topMargin=45,bottomMargin=54,title='Commitments Hidden in Conversation - Midterm Draft',author='CMSC848N Project 07 team; AI-assisted draft')
doc.build(flow,onFirstPage=footer,onLaterPages=footer)
(ROOT/'midterm_report_editable.txt').write_text(html.unescape(re.sub(r'<[^>]+>', '', '\n\n'.join(text).replace('<br/>', '\n'))))
print(ROOT/'midterm_report_draft.pdf')
