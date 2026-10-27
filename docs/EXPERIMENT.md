# Commitments Hidden in Conversation — midterm pilot

CMSC848N, Fall 2026. This package is an AI-assisted research prototype. Labels are drafts awaiting independent team review. No results should be presented as human-validated performance until that review is complete.

## Files

- `dataset_draft.json`: transcripts, original reference summaries, 66 draft answer keys, exact evidence, and rationales.
- `experiment_inputs.json`: 22 examples with questions and options; gold answers and rationales removed.
- `dataset_manifest.json`: sampling, split, source hash, and limitations.
- `ANNOTATION_GUIDE.md`: task contract, update rules, review procedure, and failure categories.
- `independent_review_template.json`: blank answers for independent review.
- `pilot.py`: cached inference orchestration, incremental ledger, baseline QA, and draft-label scoring.
- `test_pilot.py`: checks for leakage, provenance validation, split separation, caching, and scoring failures.
- `CMSC848N_Commitment_Pilot.ipynb`: self-contained Colab notebook.
- `analyze_results.py`: recomputes v0.2.0 results, errors, and inference costs without a GPU.
- `review_blind.txt` and `independent_review_template.json`: materials for two independent human reviewers.
- `review_agreement.py`: compares completed reviews and reports raw agreement.
- `build_dataset.py` and `provenance/`: exact original draft construction and sampled public source records.
- `legacy_report/build_report.py`: archived generator for the superseded standalone report. The current report is maintained in Overleaf.

## Experiment

Fixed model: Qwen/Qwen3.8-27B, revision `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`.
Target inference: NF4 4-bit weights, double quantization, BF16 compute, batch size one, thinking disabled, deterministic greedy decoding. Actual installed package versions and GPU information must be saved with the run.

For each conversation, the same model answers the same three questions from: (1) the complete selected transcript, (2) the supplied reference summary, (3) a newly generated ordinary summary, and (4) an incrementally produced ledger with revision history. Synthetic conversations have no human/reference meeting summary, so that condition is omitted rather than fabricated. The model creates summaries/records without seeing the questions or answer keys. Question wording/options are visible only in the final QA step. A fifth, question-only diagnostic supplies no conversation; it measures answer-option/prior shortcuts. It is reported separately from the four main conditions.

Generated summaries have a 512-token generation limit; ledger updates 1,536; QA 640. Real transcripts are split into contiguous chunks of at most roughly 2,200 characters at sentence/newline boundaries. Synthetic conversations are processed one speaker turn at a time. The tracker sees prior records and the new chunk; a program checks field structure and verbatim source evidence, allowing one repair attempt. All old/new snapshots are saved. This is a provenance check, not a semantic solver. No evidence validator can guarantee entailment.

The comparisons use the same model, decoding, and questions but different representation lengths and different preprocessing compute. They are not compute-matched. Save and report token counts and latency. The raw-transcript baseline is an informative full-information comparison, not a strict theoretical upper bound. No fine-tuning is performed.

## Sample and limits

The assistant sampled 30 entries from the MeetingBank validation split with seed 848, reviewed candidate content, and selected 12 for manageable length and relevant positive/negative phenomena. This purposive selection is not representative. There are 10 assistant-authored synthetic cases. Four real and two synthetic cases are development examples; eight real and eight synthetic cases form a provisional pilot split. Meetings do not cross these splits. These pilot examples do not constitute a final held-out-domain benchmark.

Report development and pilot results separately, and real versus synthetic separately. Answer accuracy against current draft keys is diagnostic only. It does not measure extraction recall or the fraction of unsupported ledger records. These require additional full-record annotation and review. No inter-annotator agreement has yet been measured.

## Local verification

```sh
python -m unittest -v test_pilot.py
```

## Reproducibility and resuming

Every completed inference call is saved under `results/calls/`, including input messages, raw output, runtime, and token counts from the model adapter. Cache keys incorporate prompts, generation limits, and model/configuration. Completed examples include states and rejected updates. Restarting with identical inputs/configuration reuses cached work. Copy or download results out of an ephemeral Colab runtime; local caching alone does not survive deletion of that runtime.

## Midterm scope

The course website's proposed rubric asks for a short report, runnable code, preliminary evidence, and an updated plan. Its printed dates are planning dates; use the deadline communicated by the instructor/user. Before submission: independently review labels, inspect source support for record errors, add verified measurements, verify related-work claims, and disclose AI assistance and each team member's actual contribution. Do not assign team contributions that have not occurred.

## Sources

- MeetingBank dataset and license (CC-BY-NC-SA-4.0): https://huggingface.co/datasets/huuuyeah/meetingbank
- Hu et al., MeetingBank: https://arxiv.org/abs/2305.17529
- Heck et al., zero-shot dialogue state tracking: https://arxiv.org/abs/2306.01386
- Rezazadeh et al., Collaborative Memory: https://arxiv.org/abs/2505.18279
- Qwen model card: https://huggingface.co/Qwen/Qwen3.8-27B
- Course rubric: https://furong-huang.com/cmsc848n-fall-2026/#project-rubrics

MeetingBank-derived excerpts and annotations retain the source's attribution/noncommercial/share-alike requirements. Synthetic examples are clearly identified; no private conversation data is used.

## Reviewing and rescoring

Two reviewers should use different copies of the blank template and `review_blind.txt`. Compare the completed files with `python review_agreement.py reviewer1.json reviewer2.json`. After discussion, produce one complete adjudicated review file and run `python score_reviewed.py adjudicated_review.json`. This preserves the original draft labels and scores and writes separate adjudicated files. Reviewers must verify the human-review procedure themselves; a script cannot certify independence.

## Runtime notes

The observed environment is recorded in `requirements-observed.txt` and the run metadata. The portable notebook pins the observed inference-library versions and retains the pinned model revision. Colab supplies PyTorch/CUDA. This initial run uses the model's correct but slower fallback linear-attention kernels; optimizing those kernels is future engineering work. The official Transformers model documentation describes the optional acceleration packages: https://huggingface.co/docs/transformers/model_doc/qwen3_5.

## Completed run (26 October 2026)

All 22 examples completed: 176 inference calls and 300 scored answers. On the real pilot, transcript / generated summary / tracker / reference summary scored 24/24, 22/24, 21/24, and 15/24; the question-only control scored 17/24. On synthetic pilot data, all three source-based methods scored 24/24 and question-only scored 10/24. These remain AI-draft-label results.

The current report is maintained separately in Overleaf. `analysis.json`, `error_audit_draft.json`, `results/`, and `environment.json` retain the measurements and raw evidence. Recompute with `python analyze_results.py`; The historical standalone report generator additionally requires reportlab.

The Colab A100 runtime was released after local backup verification with user approval. The live notebook retains the executed outputs. For a fresh run, use the self-contained notebook in this package; the archived executed notebook in `provenance/` records the original upload-based workflow. Results include earlier smoke-test cache files; `analyze_results.py` selects v0.2.0 examples and counts only their referenced calls.
