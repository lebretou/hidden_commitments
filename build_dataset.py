"""Rebuild original AI-draft labels from the archived 30-entry screening sample.
WARNING: overwrites draft labels, experiment inputs, and the blank review template.
Keep completed human review files under different names.
"""
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ROOT.mkdir(parents=True, exist_ok=True)
sample = json.loads((ROOT/'provenance'/'screening30.json').read_text())
examples = []

def question(kind, text, answer, wrong, evidence, rationale):
    assert len(wrong) == 3 and answer not in wrong
    return dict(kind=kind, text=text, answer_text=answer, options=[answer]+wrong,
                evidence_quote=evidence, rationale=rationale)

def real(index, split, questions, note):
    r = sample[index]
    examples.append(dict(id='mb_'+str(index).zfill(2), domain='meetingbank', split=split,
        source_uid=r['uid'], source_split='validation', source_row_id=r['id'],
        meeting_group='_'.join(r['uid'].split('_')[:2]), transcript=r['transcript'],
        reference_summary=r['summary'], annotation_status='AI_draft_requires_human_review',
        sampling_note=note, questions=questions))

q=question
real(0,'dev',[
 q('commitment_detection','Does this excerpt establish a personal promise by the city manager to execute the WIOA documents?',
   'No personal promise is established; authorization is discussed', ['Yes, an unconditional personal promise','Yes, a promise conditional on Friday delivery','The documents are reported as already executed'],
   'Recommendation to authorize the city manager to execute all documents','Permission or authorization does not by itself show personal acceptance.'),
 q('condition','Is a Friday delivery condition stated for executing the WIOA documents?', 'No such condition is stated', ['Yes, delivery by Friday','Yes, delivery on Monday','Yes, receipt of a revised experiment'],
   'Recommendation to authorize the city manager to execute all documents','No temporal condition of this kind occurs in the full excerpt.'),
 q('completion','Does the excerpt establish that the city manager has already executed the documents?', 'Completion is not established', ['Yes, execution is explicitly confirmed','Yes, a signed document is quoted','Yes, execution is confirmed by the contractor'],
   'Recommendation to authorize the city manager','A passed motion is not evidence of subsequent execution.')], 'Short authorization case; negative control.')

real(6,'dev',[
 q('modality','How is the March timing for the next conveyance described?', 'A target that staff think is achievable', ['A completed transfer','An unconditional guarantee of a precise date','An explicitly canceled plan'],
   "We are shooting for March, so next month we think that's very doable.",'Tentative scheduling language must not become certainty.'),
 q('condition','In the account of the transfer process, what precedes the Navy transferring property to the city?', 'Cleanup to the agreed levels', ['A Friday dataset delivery','A promise by every councilmember','Completion of every future development project'],
   "as the Navy cleans the property to the cleanup levels agreed to, they're transferring the property to the city",'This is a reported process dependency, not a new conversational promise.'),
 q('completion','Does this excerpt report that the proposed phase-two conveyance is already complete?', 'No; the conveyance is still being pursued', ['Yes; all eleven deeds have been completed','Yes; all development is complete','Yes; the March ceremony already happened'],
   'Next steps. We are shooting for March','Do not treat the approval motion as completion of the transfer.')], 'Longer tentative-plan and reported-obligation case.')

real(8,'pilot',[
 q('revision','Is the speaker still proposing to spend an hour presenting the 175-page bill?', 'No; the speaker says it was a joke and will cover highlights', ['Yes, an hour-long presentation remains promised','Yes, but only after six months','The presentation was reassigned to the mayor'],
   "That was a joke. I'm just going to go through some of the highlights.",'The explicit correction overrides the earlier apparent plan.'),
 q('deadline','When is the check-in on the remedies described as planned?', 'In about six months', ['The next day','In exactly one hour','No check-in is mentioned'],
   'a check in in about six months','Keep the approximation.'),
 q('owner','Who is stated to sign the bill after its passage?', 'The chair', ['The Office of Labor Standards director','Every business owner','No owner or role is stated'],
   'The bill passes and the chair will sign it.','A future role-based action is explicitly stated; signing is not yet confirmed.')], 'Includes correction/joke, approximate time, and procedural future action.')

real(10,'pilot',[
 q('commitment_detection','Does the hope for similar irrigation projects at all parks establish a promise to deliver them?', 'No; it is expressed as a hope', ['Yes, all parks are promised upgrades','Yes, every park is already upgraded','Yes, American Landscape accepts all future park projects'],
   'I hope we have something like this at all the parks in time.','Hope is not acceptance of responsibility.'),
 q('deadline','What deadline is promised for upgrading all parks?', 'No deadline is promised', ['This Friday','Within four years','Before the next meeting'],
   'I hope we have something like this at all the parks in time.','Do not reuse the past four-year discussion period as a future deadline.'),
 q('completion','Is completion of the Heartwell irrigation renovation established?', 'No; the discussion concerns moving forward with the project', ['Yes, installation is complete','Yes, all city parks have been renovated','Yes, final inspection is reported'],
   "We're glad to finally move forward and update the irrigation system.",'Planning and contract discussion are not completion evidence.')], 'Hope and authorization negative control; original transcript spelling preserved.')

real(17,'pilot',[
 q('condition','Under what circumstances does Modica say he remains available during furloughs?', 'Emergencies or matters that cannot reasonably wait until the next day', ['Only after all furlough days end','Only after September eight','Unconditionally for every routine task at all hours'],
   "when there's emergencies, if there's things that cannot be reasonably delayed to the next day",'Preserve the availability qualification.'),
 q('deadline','When does the speaker say the elected-official participation item will return for consideration?', 'September eight', ['September twenty-six','The next day','No date is given'],
   'that item should be in front of you back on September eight','A later sentence reinforces the return commitment.'),
 q('condition','What condition is attached to returning to general public comment near the end?', 'After the technical problem is fixed', ['Only after the next fiscal year','Only if the city manager cancels furloughs','There is no stated condition'],
   "we'll just come back the general public comment after we get it working",'The record must keep the technical dependency and the deferred action.')], 'Multiple explicit commitments and technical deferral; no diarized speaker labels.')

real(18,'pilot',[
 q('commitment_detection','Does Councilman Austin personally promise to construct the park in this excerpt?', 'No; he asks colleagues to support the project', ['Yes, he personally undertakes construction','Yes, he guarantees completion tomorrow','He reports having personally finished construction'],
   'ask my colleagues to support this','Support for authorization is not personal acceptance of construction work.'),
 q('condition','What prerequisite is stated for being in a position to start park development?', 'The site is graded and capped', ['All residents sign a petition','A dataset arrives by Friday','Councilman Austin personally buys the site'],
   'once this is graded and capped','A project dependency can be stated without a personal promise.'),
 q('completion','Does the passed motion establish that the park is already built?', 'No, construction completion is not established', ['Yes, the park is complete','Yes, every phase is finished','Yes, the park has opened'],
   'to actually started the development of a vibrant park','Future development remains distinct from the vote.')], 'Authorization plus development dependency.')

real(20,'pilot',[
 q('commitment_detection','Does thanking staff for support establish an explicit new personal task commitment?', 'No explicit new personal task commitment is established', ['Yes, staff promise to run all events','Yes, the speaker promises to organize every event','Yes, the mayor promises personal payment'],
   'I just really wanted to thank staff and my colleagues for their support on this item.','Thanks and budget support do not define an accepted task.'),
 q('completion','Does the excerpt establish that the 2021 HOPE event has already been delivered?', 'Event completion is not established', ['Yes, completion is explicitly reported','Yes, attendance is verified','Yes, the final event report is read'],
   'recommendation to increase appropriations','Budget discussion is not event completion.'),
 q('owner','Who explicitly accepts personal responsibility for organizing the HOPE event here?', 'No individual explicitly accepts that task', ['The mayor','Every councilmember','The city clerk'],
   'recommendation to increase appropriations','The transcript does not assign and accept the organizing task.')], 'Budget vote negative control.')

real(21,'dev',[
 q('modality','What is the status of reaching out to a local vehicle vendor?', 'A possibility is discussed without a commitment', ['Staff make a firm promise to contact one','A local vendor has already been contacted','The task is accepted by Councilmember Knox White'],
   'We could reach out to a local vendor','Could plus a discouraging explanation does not establish acceptance.'),
 q('completion','Had staff reached out locally for this purchase, according to the explanation?', 'No, staff explicitly say they did not', ['Yes, all local vendors were contacted','Yes, one local Toyota vendor was contacted','The transcript explicitly confirms three local bids'],
   'We did not reach out locally','This is direct evidence about a past action.'),
 q('deadline','What deadline is promised for local vendor outreach?', 'No outreach deadline is promised', ['Friday','Before tonight ends','Within three days'],
   'We could reach out to a local vendor','No accepted outreach task or deadline follows.')], 'Possibility versus commitment; explicit past non-completion.')

real(23,'pilot',[
 q('commitment_detection','Does authorizing the superintendent to amend a lease establish the superintendent personally accepting that task?', 'No personal acceptance is shown', ['Yes, the superintendent explicitly accepts','Yes, the superintendent promises to sign tomorrow','The superintendent reports completion'],
   'authorizes superintendent to amend the existing. Ten year lease.','Authority is distinct from conversational acceptance.'),
 q('completion','Does the excerpt establish that the lease amendment has been executed?', 'Execution is not established', ['Yes, the signed amendment is quoted','Yes, the superintendent confirms signing','Yes, the tenant confirms signing'],
   'authorizing superintendent to amend the existing ten year lease','Passing a bill is not executing the amendment.'),
 q('deadline','Is the five-year extension a stated deadline for executing the amendment?', 'No; it describes the additional lease term', ['Yes, it is the signing deadline','Yes, it is a five-day deadline','Yes, it is the current meeting deadline'],
   'add a third additional extended term of five years','Duration of an agreement must not be confused with an action deadline.')], 'Institutional authorization and time-type confusion.')

real(24,'pilot',[
 q('commitment_detection','Does the opening request to staff show staff accepting the arrangement task?', 'No acceptance is shown in the excerpt', ['Yes, staff explicitly accept','Yes, every staff member accepts','Yes, the task is reported completed'],
   'I just ask staff to arrange that.','Request alone, with missing antecedent, cannot establish accepted responsibility.'),
 q('deadline','How is December 18 described in the opening?', 'A tentative date', ['A guaranteed deadline','A completion date','A cancellation date'],
   "We're looking at pot probably December 18th.",'Probably preserves uncertainty despite transcript noise.'),
 q('completion','Does the grant discussion establish that the open-space restoration is complete?', 'No; the project is still described as forthcoming', ['Yes, restoration is complete','Yes, a final inspection is reported','Yes, the park opening ceremony is complete'],
   "It's going to happen. This is our first vote on it.",'An anticipated project and first vote are not evidence of completion.')], 'Missing context, tentative date, and planned project.')

real(26,'dev',[
 q('owner','Who says they will give an overview of each legislative item?', "Councilmember O'Brien", ['President Harrell','The adjacent property owner','No speaker can be linked to the overview'],
   "Councilmember O'Brien ready this topic.",'Owner inferred from the local introduction; human review should verify noisy attribution.'),
 q('modality','What is promised in response to further clarifying questions?', 'An effort to provide more details, not a guarantee of complete answers', ['A guarantee to resolve every question','A promise to buy more property','A promise to postpone all legislation'],
   "I'm happy to do my best to give you more details.",'Preserve effort-limited language.'),
 q('completion','Does the speaker report that payment for the small parcels has already occurred?', 'Yes; the speaker says the city paid for the land', ['No, payment is explicitly canceled','No, the owner refused payment','Payment is never mentioned'],
   'We paid for that land from the adjacent property owner','A reported completed action can coexist with remaining legal procedure.')], 'Explicit future presentation and reported completion.')

real(29,'pilot',[
 q('condition','What condition is stated for making the reallocated funds available to developers?', 'Council approval that night', ['A developer delivers a dataset','All future housing is already built','There is no stated condition'],
   'if if you all approve this tonight, we would make those funds available to developers','Keep the approval condition.'),
 q('condition_resolution','Is the stated council-approval condition subsequently shown as satisfied?', 'Yes; the motion carries eight zero', ['No; the motion is rejected','No; the vote is postponed','The excerpt contains no vote outcome'],
   'Motion carries eight zero.','Condition satisfaction is distinct from performing the promised action.'),
 q('completion','Does passage of the motion prove the funds have already been made available to developers?', 'No; implementation is not confirmed', ['Yes, the transfer is explicitly confirmed','Yes, developers acknowledge receipt','Yes, housing construction is complete'],
   'Members, please cast your vote. Motion carries eight zero.','A successful condition does not constitute completion evidence.')], 'Conditional institutional undertaking followed by approval, with implementation unconfirmed.')

def synthetic(n, split, turns, qs, phenomenon):
    examples.append(dict(id=f'syn_{n:02}',domain='synthetic',split=split,
        source_uid=None,source_split=None,source_row_id=None,meeting_group=f'syn_{n:02}',
        transcript='\n'.join(f'{speaker}: {text}' for speaker,text in turns),
        reference_summary=None,annotation_status='AI_authored_requires_human_review',
        sampling_note=phenomenon,questions=qs))

synthetic(1,'dev',[('Maya',"I'll run the experiment if the dataset arrives by Friday."),('Leo','The dataset will arrive Monday, not Friday.')],[
 q('owner','Who made the conditional experiment promise?','Maya',['Leo','Both speakers','Nobody'],"Maya: I'll run the experiment",'Explicit speaker.'),
 q('condition','What was the original condition?','Dataset arrival by Friday',['Arrival by Monday','No condition','A completed experiment'], 'if the dataset arrives by Friday','Original condition must remain recoverable.'),
 q('status','What is the experiment commitment at the end?','The original condition will not be met; no unconditional obligation is established',['Maya must run it regardless','Leo has accepted it','It is completed'],'The dataset will arrive Monday, not Friday.','Do not silently move the condition.')], 'Conditional promise; failed condition.')
synthetic(2,'dev',[('Noah',"I'll send the draft on Thursday."),('Noah',"Correction: I'll send it on Friday instead."),('Iris','Friday works.')],[
 q('owner','Who owns sending the draft?','Noah',['Iris','Both speakers','Nobody'],"Noah: I'll send the draft",'Explicit owner.'),
 q('deadline','What is the current deadline?','Friday',['Thursday','Monday','No deadline'],'Friday instead','Revision supersedes prior deadline.'),
 q('revision','Which date was superseded?','Thursday',['Friday','Monday','No date was superseded'],"I'll send the draft on Thursday.",'Preserve history.')], 'Explicit deadline revision.')
synthetic(3,'pilot',[('Aisha',"I'll prepare the slides."),('Aisha','Ben, could you take over?'),('Ben',"Yes, I'll prepare them."),('Aisha',"Thanks, I'm handing this to you.")],[
 q('owner','Who currently owns preparing the slides?','Ben',['Aisha','Both remain independently assigned','Nobody'],"Ben: Yes, I'll prepare them.",'Accepted reassignment.'),
 q('revision','What happened to Aisha\'s original responsibility?','It was handed over to Ben',['It was completed by Aisha','It remains unchanged','It never existed'],"I'm handing this to you.",'Explicit handover.'),
 q('completion','Are the slides reported complete?','No completion is reported',['Yes, Ben finished','Yes, Aisha finished','Yes, both finished'],"Yes, I'll prepare them.",'Future acceptance, not completion.')], 'Accepted reassignment.')
synthetic(4,'pilot',[('Eva',"I'll check the references."),('Eva','Omar, can you take that instead?'),('Omar',"I haven't decided; I'll tell you tomorrow.")],[
 q('owner','Who still owns checking the references?','Eva',['Omar','Nobody because the request cancels it','Both accepted'],"Eva: I'll check the references.",'Unaccepted reassignment does not transfer responsibility.'),
 q('commitment_detection','Has Omar accepted checking the references?','No, he has not decided',['Yes, unconditionally','Yes, after tomorrow','Yes, he has completed them'],"I haven't decided",'Uncertainty is explicit.'),
 q('deadline','What has Omar committed to doing tomorrow?','Giving his decision',['Finishing the references','Sending the final paper','Nothing at all'],"I'll tell you tomorrow.",'Separate decision promise from target task.')], 'Unaccepted reassignment; distinct promise to respond.')
synthetic(5,'pilot',[('Tara','We could ask the lab to rerun the tests.'),('Jules','That might help. Let us discuss it next week.')],[
 q('commitment_detection','Has anyone committed to rerunning the tests?','No',['Tara has','Jules has','The lab has'],'We could ask the lab to rerun the tests.','Suggestion is not acceptance.'),
 q('owner','Who owns the test rerun as an accepted task?','No accepted owner is established',['Tara','Jules','The lab'],'That might help.','Agreement about usefulness is not taking responsibility.'),
 q('deadline','Is next week a committed test-rerun deadline?','No, it refers to discussing the idea',['Yes, the tests must finish next week','Yes, the lab promised that deadline','Yes, the tests are already complete'],'Let us discuss it next week.','Distinguish discussion from execution.')], 'Suggestion and tentative discussion.')
synthetic(6,'pilot',[('Lin',"I'll upload the results by 5 p.m."),('Lin','The results are now uploaded to the shared folder.'),('Ravi','I opened the file and can see the results.')],[
 q('owner','Who undertook uploading the results?','Lin',['Ravi','Both','Nobody'],"Lin: I'll upload the results",'Explicit owner.'),
 q('status','What is the upload status at the end?','Reported complete and corroborated',['Still awaiting acceptance','Canceled','Condition failed'],'I opened the file and can see the results.','Two conversational statements support completion; no external verification claimed.'),
 q('deadline','What deadline was originally stated?','5 p.m.',['Friday','Tomorrow','No deadline'],'by 5 p.m.','Preserve original time even after completion.')], 'Completion with conversational corroboration.')
synthetic(7,'pilot',[('Nia',"I'll submit the abstract tonight."),('Nia',"I withdraw that offer; I won't submit it."),('Sol','Understood. We have no replacement yet.')],[
 q('status','What is the abstract-submission commitment now?','Canceled',['Active','Completed','Reassigned to Sol'],"I withdraw that offer; I won't submit it.",'Explicit withdrawal.'),
 q('owner','Who currently has an accepted responsibility to submit?','Nobody',['Nia','Sol','Both'],'We have no replacement yet.','No replacement assumed.'),
 q('revision','Who originally made the promise?','Nia',['Sol','Nobody','An unnamed reviewer'],"Nia: I'll submit the abstract tonight.",'Retain canceled history.')], 'Cancellation without replacement.')
synthetic(8,'pilot',[('Pavel',"I'll book the room if the budget is approved."),('Quinn','The budget has been approved.'),('Pavel',"I haven't booked the room yet.")],[
 q('owner','Who owns booking the room?','Pavel',['Quinn','Both','Nobody'],"Pavel: I'll book the room",'Explicit owner.'),
 q('condition_resolution','Is the budget condition satisfied?','Yes',['No','Unknown','There was no condition'],'The budget has been approved.','Condition update is explicit.'),
 q('status','What is the booking status?','Active and not yet completed',['Completed','Canceled','Still blocked by unapproved budget'],"I haven't booked the room yet.",'Condition satisfaction is not task completion.')], 'Satisfied condition without completion.')
synthetic(9,'pilot',[('Rosa',"I'll run the evaluation if the data arrives Friday."),('Sam','It will arrive Monday.'),('Rosa',"Then I'll run it Tuesday even with the later delivery.")],[
 q('owner','Who owns the evaluation at the end?','Rosa',['Sam','Both','Nobody'],"Rosa: Then I'll run it Tuesday",'Owner unchanged.'),
 q('deadline','When is the revised evaluation planned?','Tuesday',['Friday','Monday','No time is stated'],"I'll run it Tuesday",'Explicit new schedule.'),
 q('revision','Does the original Friday-arrival requirement still block the revised plan?','No; Rosa explicitly accepts the later delivery',['Yes; no revision was made','The evaluation is already complete','Sam has taken over'],'even with the later delivery.','Do not discard explicit revision.')], 'Failed condition followed by renewed commitment.')
synthetic(10,'pilot',[('Uma',"I might be able to review the paper, but I can't promise yet."),('Victor',"Okay, I won't count on that.")],[
 q('modality','How should Uma\'s statement be classified?','Tentative possibility with explicit noncommitment',['Firm promise','Completed review','Accepted reassignment'],"I can't promise yet.",'Preserve explicit qualification.'),
 q('owner','Who has accepted responsibility for the review?','Nobody',['Uma','Victor','Both'],"I won't count on that.",'No acceptance appears.'),
 q('completion','Is a completed review established?','No',['Yes, by Uma','Yes, by Victor','Yes, by an unnamed reviewer'],"I might be able to review the paper",'Future possibility does not establish completion.')], 'Explicit uncertainty and noncommitment.')

for ex in examples:
    for i, question in enumerate(ex['questions']):
        question['id'] = f"{ex['id']}_q{i+1}"
        assert question['evidence_quote'] in ex['transcript'], (ex['id'], question['evidence_quote'])
        random.Random(question['id']+'848').shuffle(question['options'])
        question['answer'] = 'ABCD'[question['options'].index(question['answer_text'])]
        question['options'] = dict(zip('ABCD',question['options']))
    ex['transcript_sha256'] = hashlib.sha256(ex['transcript'].encode()).hexdigest()

dev_groups={x['meeting_group'] for x in examples if x['split']=='dev'}
pilot_groups={x['meeting_group'] for x in examples if x['split']=='pilot'}
assert not dev_groups & pilot_groups
(ROOT/'dataset_draft.json').write_text(json.dumps(examples,ensure_ascii=False,indent=2))
inputs=[]
for ex in examples:
    clean={k:v for k,v in ex.items() if k!='questions'}
    clean['questions']=[{k:q[k] for k in ('id','kind','text','options')} for q in ex['questions']]
    inputs.append(clean)
(ROOT/'experiment_inputs.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2))
review=[{'example_id':x['id'],'question_id':q['id'],'reviewer':'','answer':'','evidence_quote':'','notes':''} for x in examples for q in x['questions']]
(ROOT/'independent_review_template.json').write_text(json.dumps(review,indent=2))
manifest={'version':'pilot-v0.1','seed':848,'annotation_status':'AI-authored draft; not independently human-validated',
 'dataset_url':'https://huggingface.co/datasets/huuuyeah/meetingbank','license':'CC-BY-NC-SA-4.0 (MeetingBank-derived data)',
 'source_file_sha256':'efd90b86345fe7d75d44502ae394d352e977956b2a3983df11ea8a25cd78bf99',
 'source_split':'validation','screened_random_sample':30,'selected_real':12,'synthetic':10,'questions':sum(len(x['questions']) for x in examples),
 'selection':'Random seed 848 selects 30 validation entries. Twelve are manually inspected by the assistant and purposively selected for length and phenomena. This is not a representative random evaluation sample.',
 'split':'4 real + 2 synthetic development; 8 real + 8 synthetic pilot. Grouped by source meeting. Pilot is provisional, not a final held-out benchmark.',
 'limitations':['No human agreement measured','Synthetic cases authored by the assistant','Reference summaries are not available for synthetic cases','MeetingBank text is noisy and not diarized','QA probes are not exhaustive commitment annotations']}
(ROOT/'dataset_manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
