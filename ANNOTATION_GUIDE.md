# Commitment pilot annotation guide v0.1

This is an AI-assisted draft for team review, not a human-validated gold standard.

## Task contract

Given a conversation prefix, identify what a speaker or institution has undertaken to do, any conditions and time qualifications, the currently supported status, and the utterances that justify that interpretation. Never use later turns for an earlier snapshot. A correct record may be uncertain or have an unknown owner.

The pilot includes task-specific multiple-choice probes. These are not exhaustive commitment annotations. Consequently, QA accuracy must not be described as commitment extraction precision/recall or F1.

## Speech-act distinctions

| Category | Operational rule | Example |
|---|---|---|
| Suggestion | An action is proposed without anyone accepting responsibility. | “We could rerun the tests.” |
| Intention | A speaker expresses a plan or goal with limited assurance. | “We are shooting for March.” |
| Firm commitment | The speaker accepts or explicitly undertakes an action. | “I will send it Friday.” |
| Conditional commitment | An undertaking depends on an explicit prerequisite. | “I will send it if the review is approved.” |
| Uncertain | Multiple readings remain plausible or attribution is unclear. | “I can do that,” without enough context to tell ability from acceptance. |
| Reported obligation | A speaker describes an institution's or third party's responsibility. | “The chair will sign the bill.” |
| No task commitment | Permission, hopes, appreciation, historical facts, or mere discussion do not establish acceptance. | “Authorize the manager to execute the agreement.” |

Reported obligations may be retained with a qualification saying they are reported rather than personally accepted. Requests and authorizations remain separate from the target's acceptance. Procedural commitments (e.g., returning to public comment) are in scope for this pilot; generic statements about laws or policy effects are not automatically commitments.

## Record fields

- `id`: stable within one conversation; revisions reuse the same ID.
- `owner`: supported name, role, or institution; otherwise null. Do not invent a name from world knowledge.
- `action`: the undertaken action, retaining meaningful qualifiers.
- `conditions`: prerequisites and exceptions, or null if none stated. Unknown and unstated must be explained where relevant.
- `deadline`: stated action time, preserving “about,” “probably,” and similar qualifications. A lease term is not a signing deadline.
- `status`: suggested, intended, conditional, active, condition_failed, completed, cancelled, or uncertain.
- `uncertainty`: explanation of ambiguous interpretation, noisy attribution, reported responsibility, or limited scope.
- `evidence`: exact source quotations. The implementation adds character offsets automatically.
- `history`: previous and revised versions plus supporting update evidence.

## Update rules

1. Keep the original condition unless an explicit revision changes it. A delayed dataset does not silently move a Friday condition to Monday.
2. Condition satisfaction changes whether an undertaking applies; it does not establish that the task is complete.
3. An explicit withdrawal cancels a commitment. A request to reassign it does not cancel or transfer it without adequate acceptance/handover evidence.
4. Completion needs an explicit report or other supplied evidence. Label conversationally reported completion as such; do not claim external verification.
5. Preserve superseded dates and owners in history. Distinguish corrections, jokes, and renewed undertakings.
6. Do not convert votes, authorization, support, or thanks into a personal promise. Institutional decisions can be recorded separately or qualified.
7. Leave unclear speech unclear. Do not repair noisy transcripts by silently adding facts. Use local introductions for speaker attribution only when supported.
8. Keep target tasks separate: promising to decide tomorrow is not promising to perform the requested task tomorrow.

## Independent review procedure

Two team members should independently read `experiment_inputs.json` and fill separate copies of `independent_review_template.json` before seeing `dataset_draft.json`. Use option letters A–D, exact evidence, and brief ambiguity notes. For at least a shared subset, compute raw answer agreement before adjudication with `review_agreement.py`; report the number of questions and conversations. Do not compute semantic-category kappa from shuffled A-D options. Later, compute Cohen's kappa on independently assigned shared speech-act categories for aligned candidate records. Reconcile disagreements by discussion, preserve both originals, and version the adjudicated labels. Do not count the assistant's checks as a second human annotator.

For exhaustive record evaluation later, annotators must additionally identify all candidate commitments and align records across annotations before field-level agreement is meaningful.

## Failure taxonomy

| Code | Error |
|---|---|
| F1 | Suggestion, hope, request, or permission promoted to a firm commitment |
| F2 | Wrong or invented owner |
| F3 | Dropped, changed, or overgeneralized condition |
| F4 | Missed revision, cancellation, joke, or accepted reassignment |
| F5 | Approval or intention mistaken for completion |
| F6 | Unsupported certainty, invented deadline, or time-type confusion |
| F7 | Unsupported quotation or evidence that does not entail the claim |
| F8 | Malformed output, rejected update, or lost state |
| F9 | Necessary information omitted from a summary |

An exact matching quotation verifies provenance only. It does not prove the quote entails the record. Inspect that manually.
