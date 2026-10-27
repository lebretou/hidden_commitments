# Commitments Hidden in Conversation

CMSC848N class project. We test whether a structured record of owners, actions, conditions, revisions, and evidence preserves commitments better than an ordinary summary.

The prototype and first experiment are complete. **Answer keys and synthetic conversations are AI-drafted and still need independent human review.** The pilot does not establish an advantage for the tracker.

## Start here

- **Review the answers:** download or clone this repository, then open [`review/review.html`](review/review.html) in a desktop browser. Read [`review/START-HERE.txt`](review/START-HERE.txt). Each reviewer exports a separate JSON file. The form works offline.
- **Inspect the experiment:** read [`docs/EXPERIMENT.md`](docs/EXPERIMENT.md) and [`ANNOTATION_GUIDE.md`](ANNOTATION_GUIDE.md).
- **Reproduce the analysis:** run the commands below. No GPU or extra Python packages are required for these checks.
- **Run new inference:** open [`CMSC848N_Commitment_Pilot.ipynb`](CMSC848N_Commitment_Pilot.ipynb) in Colab and select an A100. The notebook includes its runtime files and installs the pinned inference dependencies. Save results before releasing the runtime.

The current report, bibliography, and two report figures are maintained separately in [Overleaf](https://www.overleaf.com/project/6adf9f0e68ca935aaae7569c). This repository does not contain that Overleaf project.

## Local setup and checks

Python 3.10 or newer is sufficient for the standard-library checks; the original runtime used Python 3.12. From this repository folder:

```sh
python3 -m unittest -v test_pilot.py
python3 verify_saved_run.py
python3 analyze_results.py
```

`verify_saved_run.py` reconstructs all 22 completed examples from cached model calls in a temporary folder and fails if a model call would be needed. It compares the reconstructed results and scores with the saved run. `analyze_results.py` regenerates `analysis.json` from the draft labels and saved outputs.

## What is included

| Path | Purpose |
| --- | --- |
| `pilot.py` | Tracker, baselines, evidence checks, caching, and scoring |
| `load_model.py`, `colab_run.py` | Pinned Qwen3.8-27B Colab inference |
| `CMSC848N_Commitment_Pilot.ipynb` | Self-contained runnable notebook |
| `build_notebook.py` | Rebuild the notebook from the current source files |
| `build_dataset.py` | Rebuild the original draft dataset from archived sources; overwrites draft files |
| `dataset_draft.json` | Conversations plus draft answers, evidence, and rationales |
| `experiment_inputs.json` | Model inputs with answer keys removed |
| `dataset_manifest.json` | Sampling, splits, attribution, and limitations |
| `results/` | Original model outputs, tracker states, and inference cache |
| `analysis.json`, `error_audit_draft.json` | Preliminary scores and inspected failure cases |
| `provenance/` | Sampled source records, executed notebook/runtime, and original export checksums |
| `review/` | Offline review form, instructions, and plain-text fallback |
| `review/source/` | Reproducible review-form builder and HTML template |
| `review_agreement.py`, `score_reviewed.py` | Compare reviews and rescore saved model answers |
| `legacy_report/` | Earlier standalone report generator, retained as historical code; not the current Overleaf report |

The old chat exports remain snapshots. Use this repository as the working codebase. `provenance/original_export_checksums.json` describes the original export, including files that are not in this repository; it is not a checksum manifest of the reorganized repository.

## Pilot results

Twelve public meeting excerpts and ten synthetic conversations contain three questions each. Six conversations are development examples; the main pilot has eight real and eight synthetic conversations.

| Information given to the model | Real pilot | Synthetic pilot |
| --- | ---: | ---: |
| Full transcript | 24/24 | 24/24 |
| Generated summary | 22/24 | 24/24 |
| Structured tracker | 21/24 | 24/24 |
| Supplied reference summary | 15/24 | Not available |
| Questions only | 17/24 | 10/24 |

These are question-answering scores against draft keys, not commitment-extraction accuracy. The high questions-only score reveals weaknesses in the probes. A correct answer can also hide an incorrect stored record.

The completed run used Qwen/Qwen3.8-27B in NF4 4-bit mode on a Colab A100 40 GB, with 176 unique inference calls and 18.37 GiB peak allocated GPU memory. Exact versions are in `requirements-observed.txt` and `environment.json`. No fine-tuning was performed.

## Independent review and rescoring

Review the same items independently with at least two human reviewers before comparing answers. Do not open `dataset_draft.json`, `analysis.json`, model outputs, or the draft-key files during blind review. The offline form excludes those materials, but the repository retains them for reproducibility. If a reviewer has already seen a result or key, record that exposure in the form.

Save individual exports under `reviews/` (ignored by Git by default) and retain the originals. Inspect uncertainty, discussion, and prior-exposure flags before calculating agreement. The current comparison script reports raw A–D answer agreement and does not interpret those flags automatically.

```sh
python3 review_agreement.py reviews/reviewer1.json reviews/reviewer2.json
python3 score_reviewed.py reviews/adjudicated.json
```

The rescoring script requires all 66 adjudicated A–D answers. Do not force a choice on an unresolvable question: define a separate subset evaluation and report its denominator instead. Rescoring writes new adjudicated files and preserves the original draft labels and scores. A GPU rerun is unnecessary.

To rebuild the browser form or portable notebook after intentional source changes:

```sh
python3 review/source/build_packet.py
python3 build_notebook.py
```

## Attribution and project status

MeetingBank-derived data comes from [huuuyeah/meetingbank](https://huggingface.co/datasets/huuuyeah/meetingbank), under its CC-BY-NC-SA-4.0 terms. Retain attribution and applicable noncommercial/share-alike requirements. Source identifiers and hashes are preserved in the manifests and provenance files. Synthetic conversations are identified separately. No private conversations are included.

Codex assisted with the implementation, draft annotations, synthetic examples, and documentation. Independent human annotation and agreement measurement have not yet been completed. Team members should review the labels and claims before submission.
